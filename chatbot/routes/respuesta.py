from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot.semhash import responder,Conocimiento,Entidad
from chatbot import app, mongo



@app.route('/obtenerRespuestaAlumno',methods=['GET','POST'])
def obtenerRespuesta():
  data = request.get_json()
  consulta = data['consulta']
  tema_id = data['tema_id']
  alumno_id = data['alumno_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimientos = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})
  coleccionEntidad = mongo.db.entidad
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})
  coleccionAlumno = mongo.db.alumno
  alumno = coleccionAlumno.find_one({'_id':ObjectId(alumno_id)})

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})


  conocimientosBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 

  entidadBD = []
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))

  
  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, alumno)

  if(respuesta in ['texto','importancia','explicacion','ejemplos','quiz','imagen','documento','video']):
    respuesta = {
      'respuesta_item': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }
  else:
    respuesta = {
      'respuesta': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }

  return jsonify(respuesta)

@app.route('/obtenerRespuestaProfesor',methods=['GET','POST'])
def obtenerRespuestaProfesor():
  data = request.get_json()
  consulta = data['consulta']
  tema_id = data['tema_id']
  profesor_id = data['profesor_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimientos = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})
  coleccionEntidad = mongo.db.entidad
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})
  coleccionProfesor = mongo.db.profesor
  profesor = coleccionProfesor.find_one({'_id':ObjectId(profesor_id)})

  conocimientosBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 

  entidadBD = []
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))

  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, profesor)
  
  if(respuesta in ['texto','importancia','explicacion','ejemplos','quiz','imagen','documento','video']):
    respuesta = {
      'respuesta_item': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }
  else:
    respuesta = {
      'respuesta': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }

  return jsonify(respuesta)

def procesamientoCategoriaMaterial(tema_id):
  conocimientosBDAux = []

  coleccionMaterial = mongo.db.material
  materiales = coleccionMaterial.find({'tema_id': ObjectId(tema_id)})

  recursos = []

  for material in list(materiales):
    obj_dict = {}
    obj_dict['nombre']=material['nombre']
    obj_dict['material']=str(material['_id'])
    obj_dict['faq']=material['faq']

    recursos.append(obj_dict)
  
  for recurso in recursos:
    arreglo_recurso = []

    dict_texto = {}
    preguntas = ['Que es '+recurso['nombre']]
    respuestas = ['texto']
    material = recurso['material']
    dict_texto['preguntas'] = preguntas
    dict_texto['respuestas'] = respuestas
    dict_texto['material_id'] = material
    arreglo_recurso.append(dict_texto)
  
    dict_importancia = {}
    preguntas = ['Por que es importante '+recurso['nombre']]
    respuestas = ['importancia']
    material = recurso['material']
    dict_importancia['preguntas'] = preguntas
    dict_importancia['respuestas'] = respuestas
    dict_importancia['material_id'] = material
    arreglo_recurso.append(dict_importancia)

    dict_explicacion = {}
    preguntas = ['Donde encuentro mas informacion de '+recurso['nombre']]
    respuestas = ['explicacion']
    material = recurso['material']
    dict_explicacion['preguntas'] = preguntas
    dict_explicacion['respuestas'] = respuestas
    dict_explicacion['material_id'] = material
    arreglo_recurso.append(dict_explicacion)
  
    dict_ejemplos = {}
    preguntas = ['Dime ejemplos de '+recurso['nombre']]
    respuestas = ['ejemplos']
    material = recurso['material']
    dict_ejemplos['preguntas'] = preguntas
    dict_ejemplos['respuestas'] = respuestas
    dict_ejemplos['material_id'] = material
    arreglo_recurso.append(dict_ejemplos)

    dict_quiz = {}
    preguntas = ['Hazme preguntas de '+recurso['nombre']]
    respuestas = ['quiz']
    material = recurso['material']
    dict_quiz['preguntas'] = preguntas
    dict_quiz['respuestas'] = respuestas
    dict_quiz['material_id'] = material
    arreglo_recurso.append(dict_quiz)

    dict_imagen = {}
    preguntas = ['Muestrame una imagen de '+recurso['nombre']]
    respuestas = ['imagen']
    material = recurso['material']
    dict_imagen['preguntas'] = preguntas
    dict_imagen['respuestas'] = respuestas
    dict_imagen['material_id'] = material    
    arreglo_recurso.append(dict_imagen)

    dict_documento = {}
    preguntas = ['Muestrame una documento de '+recurso['nombre']]
    respuestas = ['documento']
    material = recurso['material']
    dict_documento['preguntas'] = preguntas
    dict_documento['respuestas'] = respuestas
    dict_documento['material_id'] = material
    arreglo_recurso.append(dict_documento)

    dict_video = {}
    preguntas = ['Muestrame un video de '+recurso['nombre']]
    respuestas = ['video']
    material = recurso['material']
    dict_video['preguntas'] = preguntas
    dict_video['respuestas'] = respuestas
    dict_video['material_id'] = material
    arreglo_recurso.append(dict_video)

    for preguntaFrecuente in recurso['faq']:
      dict_faq = {}
      preguntas = [preguntaFrecuente['pregunta']]
      respuestas = [preguntaFrecuente['respuesta']]
      dict_faq['preguntas'] = preguntas
      dict_faq['respuestas'] = respuestas
      dict_faq['material_id'] = ''
      arreglo_recurso.append(dict_faq)

    for item in arreglo_recurso:
      aux = ObjectId()
      conocimientosBDAux.append(Conocimiento(aux,item['preguntas'],item['respuestas'],item['material_id']))
    
  return conocimientosBDAux