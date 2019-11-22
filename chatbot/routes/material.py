from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/obtenerMaterialPorTema', methods=['GET','POST'])
def obtenerListadoMaterial():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionMaterial = mongo.db.material
  
  materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})

  materiales = dumps(materiales)

  return jsonify(materiales)

@app.route('/obtenerMaterialPorId', methods=['GET','POST'])
def obtenerMaterialPorId():
  data = request.get_json()
  
  material_id = data['material_id']

  coleccionMaterial = mongo.db.material
  
  material = coleccionMaterial.find_one({'_id':ObjectId(material_id)})
  
  respuesta = {
    'material_id': str(material['_id']),
    'tema_id': str(material['tema_id']),
    'nombre': material['nombre'],
    'texto': material['texto'],
    'documento': material['documento'],
    'video': material['video'],
    'imagen': material['imagen'],
    'quiz': material['quiz'],
    'ejemplos': material['ejemplos'],
    'importancia': material['importancia'],
    'explicacion': material['explicacion'],
    'faq': material['faq']
  }
  
  return jsonify(respuesta)

@app.route('/obtenerMaterialPorAlumnoId', methods=['GET','POST'])
def obtenerMaterialPorAlumnoId():
  data = request.get_json()

  alumno_id = data['alumno_id']
  material_id = data['material_id']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  coleccionMaterial = mongo.db.material
  material = coleccionMaterial.find_one({'_id':ObjectId(material_id)})
    
  if estiloAprendizaje['procesamiento']['valor']<=3 :
    activo=estiloAprendizaje['procesamiento']['valor']
    reflexivo=estiloAprendizaje['procesamiento']['valor']
  else:
    if estiloAprendizaje['procesamiento']['categoria']=='activo' :
      activo=estiloAprendizaje['procesamiento']['valor']
      reflexivo=0
    else:
      activo=0
      reflexivo=estiloAprendizaje['procesamiento']['valor']
    
  if estiloAprendizaje['percepcion']['valor']<=3 :
    sensorial=estiloAprendizaje['percepcion']['valor']
    intuitivo=estiloAprendizaje['percepcion']['valor']
  else:
    if estiloAprendizaje['percepcion']['categoria']=='intuitivo' :
      sensorial=0
      intuitivo=estiloAprendizaje['percepcion']['valor']
    else:
      sensorial=estiloAprendizaje['percepcion']['valor']
      intuitivo=0


  if estiloAprendizaje['entrada']['valor']<=3 :
    verbal=estiloAprendizaje['entrada']['valor']
    visual=estiloAprendizaje['entrada']['valor']
  else:
    if estiloAprendizaje['entrada']['categoria']=='visual' :
      verbal=0
      visual=estiloAprendizaje['entrada']['valor']
    else:
      verbal=estiloAprendizaje['entrada']['valor']
      visual=0


  if estiloAprendizaje['comprension']['valor']<=3 :
    secuencial=estiloAprendizaje['comprension']['valor']
    _global=estiloAprendizaje['comprension']['valor']
  else:
    if estiloAprendizaje['comprension']['categoria']=='secuencial' :
      secuencial=estiloAprendizaje['comprension']['valor']
      _global=0
    else:
      secuencial=0
      _global=estiloAprendizaje['comprension']['valor']

  recursosD = {}
  prioridad = []

  recursosD['tema_id']=str(material['tema_id'])
  recursosD['nombre']=material['nombre']  

  if(sensorial or secuencial or _global):
    recursosD['texto']=material['texto']
    dictTexto = {}
    dictTexto['item']='texto'
    dictTexto['puntaje']=max(sensorial,secuencial,_global)
    prioridad.append(dictTexto)

  if(intuitivo or verbal or reflexivo or secuencial):
    recursosD['importancia']=material['importancia']
    dictImportancia = {}
    dictImportancia['item']='importancia'
    dictImportancia['puntaje']=max(intuitivo,verbal,reflexivo,secuencial)
    prioridad.append(dictImportancia)

  if(intuitivo or _global):
    recursosD['explicacion']=material['explicacion']
    dictExplicacion = {}
    dictExplicacion['item']='explicacion'
    dictExplicacion['puntaje']=max(intuitivo,_global)
    prioridad.append(dictExplicacion)

  if(sensorial or activo or secuencial):
    recursosD['ejemplos']=material['ejemplos']
    dictEjemplos = {}
    dictEjemplos['item']='ejemplos'
    dictEjemplos['puntaje']=max(sensorial,activo,secuencial)
    prioridad.append(dictEjemplos)

  if(activo or secuencial):
    recursosD['quiz']=material['quiz']
    dictQuiz = {}
    dictQuiz['item']='quiz'
    dictQuiz['puntaje']=max(activo,secuencial)
    prioridad.append(dictQuiz)

  if(intuitivo or visual):
    recursosD['imagen']=material['imagen']
    dictImagen = {}
    dictImagen['item']='imagen'
    dictImagen['puntaje']=max(intuitivo,visual)
    prioridad.append(dictImagen)

  if(verbal):
    recursosD['documento']=material['documento']
    dictDocumento = {}
    dictDocumento['item']='documento'
    dictDocumento['puntaje']=verbal
    prioridad.append(dictDocumento)
      
  if(visual):
    recursosD['video']=material['video']
    dictVideo = {}
    dictVideo['item']='video'
    dictVideo['puntaje']=visual
    prioridad.append(dictVideo)

  if(sensorial or verbal or activo):
    recursosD['faq']=material['faq']
    dictFaq = {}
    dictFaq['item']='faq'
    dictFaq['puntaje']=max(sensorial,verbal,activo)
    prioridad.append(dictFaq)

  recursosD['prioridad']=prioridad

  return jsonify(recursosD)


@app.route('/ingresarMaterial', methods=['GET','POST'])
def ingresarMaterial():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  texto = data['texto']
  documento = data['documento']
  video = data['video']
  imagen = data['imagen']
  quiz = data['quiz'],
  ejemplos = data['ejemplos']
  importancia = data['importancia']

  try:
    explicacion = data['explicacion']
    faq = data['faq']
  except:
    explicacion = []
    faq = []

  coleccionMaterial = mongo.db.material

  materialIngresado = coleccionMaterial.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'texto': texto,
    'documento': documento,
    'video': video,
    'imagen': imagen,
    'quiz': quiz,
    'ejemplos': ejemplos,
    'importancia': importancia,
    'explicacion': explicacion,
    'faq': faq
  }).inserted_id

  material = {
    'material_id': str(materialIngresado)
  }

  return jsonify(material)

@app.route('/actualizarMaterial', methods=['GET','POST'])
def actualizarMaterial():
  data = request.get_json()

  material_id = data['material_id']

  tema_id = data['tema_id']
  nombre = data['nombre']
  texto = data['texto']
  documento = data['documento']
  video = data['video']
  imagen = data['imagen']
  quiz = data['quiz']
  ejemplos = data['ejemplos']
  importancia = data['importancia']
  
  try:
    explicacion = data['explicacion']
    faq = data['faq']
  except:
    explicacion = []
    faq = []

  coleccionMaterial = mongo.db.material

  resultado = coleccionMaterial.update_one(
    {'_id':ObjectId(material_id)},
    {'$set':
              {
                'tema_id': ObjectId(tema_id),
                'nombre': nombre,
                'texto': texto,
                'documento': documento,
                'video': video,
                'imagen': imagen,
                'quiz': quiz,
                'ejemplos': ejemplos,
                'importancia': importancia,
                'explicacion': explicacion,
                'faq': faq
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarMaterial', methods=['GET','POST'])
def eliminarMaterial():
  data = request.get_json()

  material_id = data['material_id']

  coleccionMaterial = mongo.db.material

  resultado = coleccionMaterial.delete_one({'_id': ObjectId(material_id)})
   
  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)