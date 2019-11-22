from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/ingresarTema', methods=['GET','POST'])
def ingresarTema():
  data = request.get_json()

  curso_id = data['curso_id']
  nombre = data['nombre']

  coleccionTema = mongo.db.tema

  temaIngresado = coleccionTema.insert_one({
    'curso_id': ObjectId(curso_id),
    'nombre': nombre
  }).inserted_id

  nuevoTema_id = dumps(temaIngresado)

  return jsonify(nuevoTema_id)


@app.route('/obtenerTema', methods=['GET','POST'])
def obtenerTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionTema = mongo.db.tema

  tema = coleccionTema.find({"_id":ObjectId(tema_id)})

  tema = dumps(tema)

  return jsonify(tema)

@app.route('/obtenerTemaPorCurso', methods=['POST'])
def obtenerTemaPorCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionTema = mongo.db.tema

  temas = coleccionTema.find({"curso_id":ObjectId(curso_id)})

  temas = dumps(temas)

  return jsonify(temas)
