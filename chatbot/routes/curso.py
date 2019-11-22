from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo

@app.route('/obtenerCursoPorProfesor', methods=['POST'])
def obtenerCursoPorProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionCurso = mongo.db.curso

  cursos = coleccionCurso.find({'profesor_id':ObjectId(profesor_id)})

  cursos = dumps(cursos)

  return jsonify(cursos)

@app.route('/obtenerCursoPorAlumno', methods=['POST'])
def obtenerCursoPorAlumno():
  data = request.get_json()
  alumno_id = data['alumno_id']

  coleccionMatricula = mongo.db.matricula
  coleccionCurso = mongo.db.curso
  cursos = []

  matriculas = coleccionMatricula.find({'alumno_id':ObjectId(alumno_id)})
  
  for elemento in list(matriculas):
    cursos.append(coleccionCurso.find_one({'_id':ObjectId(elemento['curso_id'])}))

  return jsonify(dumps(cursos))

@app.route('/ingresarCurso',methods=['POST'])
def ingresarCurso():
  data = request.get_json()

  profesor_id = data['profesor_id']
  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  cursoIngresado = coleccionCurso.insert_one({
    'profesor_id': ObjectId(profesor_id),
    'nombre': nombre
  }).inserted_id

  curso = {
    'curso_id': str(cursoIngresado)
  }

  return jsonify(curso)

@app.route('/actualizarCurso',methods=['POST'])
def actualizarCurso():
  data = request.get_json()

  curso_id = data['curso_id']
  profesor_id = data['profesor_id']
  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  resultado = coleccionCurso.update_one(
    {'_id': ObjectId(curso_id)},
    {'$set':  
              {
                'profesor_id': ObjectId(profesor_id),
                'nombre': nombre
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarCurso',methods=['POST'])
def eliminarCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionCurso = mongo.db.curso

  resultado = coleccionCurso.delete_one({'_id': ObjectId(curso_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)