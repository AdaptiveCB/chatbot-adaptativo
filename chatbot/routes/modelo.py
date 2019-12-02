from flask import request, jsonify, redirect
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot.semhash import cargarModelo,entrenarModelo,Conocimiento,cargarVariosModelos
from chatbot import app, mongo


@app.route('/entrenar',methods=['GET','POST'])
def entrenar():
  # print('INICIO DE ENTRENAR')
  data = request.get_json()
  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({
    'tema_id' : ObjectId(tema_id)  
  })

  conocimientosBD = []

  for elemento in list(conocimiento):
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas'],elemento['material_id']))

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))

  score = entrenarModelo(conocimientosBD,tema_id)
  # print('score:',score)

  # print('FIN DE ENTRENAR')

  return str(score)


# CARGAR MODELO
@app.route('/cargar',methods=['GET','POST'])
def cargar():
  data = request.get_json()

  tema_id = data['tema_id']
  
  cargarModelo(tema_id)

  return "Modelo cargado"

@app.route('/cargarVarios',methods=['GET','POST'])
def cargarVarios():
  coleccionTema = mongo.db.tema

  temas = coleccionTema.find()

  temas = list(temas)

  temas = [str(tema_id['_id']) for tema_id in temas]

  cargarVariosModelos(temas)

  return "ok"

cargarVarios()

def procesamientoCategoriaMaterial(tema_id):
  conocimientosBDAux = []

  coleccionMaterial = mongo.db.material
  materiales = coleccionMaterial.find({'tema_id': ObjectId(tema_id)})

  coleccionPreguntaMaterial = mongo.db.preguntaMaterial
  preguntaMaterial = coleccionPreguntaMaterial.find_one({})

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
    preguntas = [preguntaMaterial['texto'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['texto']
    material = recurso['material']
    dict_texto['preguntas'] = preguntas
    dict_texto['respuestas'] = respuestas
    dict_texto['material_id'] = material
    arreglo_recurso.append(dict_texto)
  
    dict_importancia = {}
    preguntas = [preguntaMaterial['importancia'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['importancia']
    material = recurso['material']
    dict_importancia['preguntas'] = preguntas
    dict_importancia['respuestas'] = respuestas
    dict_importancia['material_id'] = material
    arreglo_recurso.append(dict_importancia)

    dict_explicacion = {}
    preguntas = [preguntaMaterial['explicacion'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['explicacion']
    material = recurso['material']
    dict_explicacion['preguntas'] = preguntas
    dict_explicacion['respuestas'] = respuestas
    dict_explicacion['material_id'] = material
    arreglo_recurso.append(dict_explicacion)
  
    dict_ejemplos = {}
    preguntas = [preguntaMaterial['ejemplos'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['ejemplos']
    material = recurso['material']
    dict_ejemplos['preguntas'] = preguntas
    dict_ejemplos['respuestas'] = respuestas
    dict_ejemplos['material_id'] = material
    arreglo_recurso.append(dict_ejemplos)

    dict_quiz = {}
    preguntas = [preguntaMaterial['quiz'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['quiz']
    material = recurso['material']
    dict_quiz['preguntas'] = preguntas
    dict_quiz['respuestas'] = respuestas
    dict_quiz['material_id'] = material
    arreglo_recurso.append(dict_quiz)

    dict_imagen = {}
    preguntas = [preguntaMaterial['imagen'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['imagen']
    material = recurso['material']
    dict_imagen['preguntas'] = preguntas
    dict_imagen['respuestas'] = respuestas
    dict_imagen['material_id'] = material    
    arreglo_recurso.append(dict_imagen)

    dict_documento = {}
    preguntas = [preguntaMaterial['documento'].replace('@','').strip() + ' ' + recurso['nombre']]
    respuestas = ['documento']
    material = recurso['material']
    dict_documento['preguntas'] = preguntas
    dict_documento['respuestas'] = respuestas
    dict_documento['material_id'] = material
    arreglo_recurso.append(dict_documento)

    dict_video = {}
    preguntas = [preguntaMaterial['video'].replace('@','').strip() + ' ' + recurso['nombre']]
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