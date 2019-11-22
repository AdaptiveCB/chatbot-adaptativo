from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/ingresarConocimiento',methods=['GET','POST'])
def ingresarConocimiento():
  data = request.get_json()

  tema_id = data['tema_id']
  material_id = data['material_id']
  preguntas = data['preguntas']
  respuestas = data['respuestas']

  coleccionConocimiento = mongo.db.conocimiento

  nuevoConocimiento = coleccionConocimiento.insert_one({
    "tema_id" : ObjectId(tema_id),
    "material_id": ObjectId(material_id) if material_id != '' else '',
    "preguntas" : preguntas,
    "respuestas" : respuestas,
  }).inserted_id

  conocimiento = {
    'conocimiento_id': str(nuevoConocimiento)
  }

  return jsonify(conocimiento)

@app.route('/actualizarConocimiento',methods=['POST'])
def actualizarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']

  tema_id = data['tema_id']
  material_id = data['material_id']
  preguntas = data['preguntas']
  respuestas = data['respuestas']

  coleccionConocimiento = mongo.db.conocimiento

  resultado = coleccionConocimiento.update_one(
    {'_id': ObjectId(conocimiento_id)},
    {'$set':  
              {
                'tema_id': ObjectId(tema_id),
                'material_id': ObjectId(material_id) if material_id != '' else '',
                'preguntas': preguntas,
                'respuestas': respuestas,
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarConocimiento', methods=['POST'])
def eliminarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']

  coleccionConocimiento = mongo.db.conocimiento

  resultado = coleccionConocimiento.delete_one({'_id':ObjectId(conocimiento_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

@app.route('/obtenerConocimientoPorTema',methods=['GET','POST'])
def obtenerConocimiento():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  conocimiento = dumps(conocimiento)

  return jsonify(conocimiento)