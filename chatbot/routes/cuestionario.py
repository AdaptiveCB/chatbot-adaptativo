from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/ingresarCuestionario', methods=['GET','POST'])
def ingresarCuestionario():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  preguntas = data['preguntas']
  nivel = data['nivel']
  tiempo = data['tiempo']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarioIngresado = coleccionCuestionario.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'preguntas': preguntas,
    'nivel': nivel,
    'tiempo': tiempo
  }).inserted_id

  cuestionario = {
    'cuestionario_id': str(cuestionarioIngresado)
  }

  return jsonify(cuestionario)

@app.route('/obtenerCuestionarioPorTema', methods=['POST'])
def obtenerCuestionarioPorTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarios = coleccionCuestionario.find({"tema_id":ObjectId(tema_id)})

  listaCuestionario = []

  for cuestionario in list(cuestionarios):
    objetoCuestionario = {}
    objetoCuestionario['cuestionario_id'] = str(cuestionario['_id'])
    objetoCuestionario['nombre'] = cuestionario['nombre']
    objetoCuestionario['preguntas'] = cuestionario['preguntas']
    objetoCuestionario['nivel'] = cuestionario['nivel']
    objetoCuestionario['tiempo'] = cuestionario['tiempo']
    listaCuestionario.append(objetoCuestionario)

  return jsonify(listaCuestionario)

@app.route('/actualizarCuestionario', methods=['GET','POST'])
def actualizarCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  nombre = data['nombre']
  preguntas = data['preguntas']
  nivel = data['nivel']
  tiempo = data['tiempo']

  coleccionCuestionario = mongo.db.cuestionario

  resultado = coleccionCuestionario.update_one(
    {'_id':ObjectId(cuestionario_id)},
    {'$set':
              {
                'nombre': nombre,
                'preguntas': preguntas,
                'nivel': nivel,
                'tiempo': tiempo
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarCuestionario',methods=['POST'])
def eliminarCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  coleccionCuestionario = mongo.db.cuestionario

  resultado = coleccionCuestionario.delete_one({'_id': ObjectId(cuestionario_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)