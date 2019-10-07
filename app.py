from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
from semhash import cargarModelo,entrenarModelo,responder,Conocimiento,cargarVariosModelos
import pandas as pd
import random

import os
# http://api.mongodb.com/python/current/api/bson/json_util.html?highlight=json_util
from bson.json_util import dumps
from bson.objectid import ObjectId




app = Flask(__name__)

CORS(app)

app.config['MONGO_DBNAME'] = 'chatbot'
app.config['MONGO_URI'] = 'mongodb+srv://chatbot:adaptive@cluster0-k4fnb.mongodb.net/chatbot?retryWrites=true&w=majority'
# app.config['MONGO_URI'] = 'mongodb://localhost/chatbot'

mongo = PyMongo(app)


@app.route('/')
def home():
  return render_template('home.html')

@app.route('/test')
def test():
  return render_template('test.html')


# MATERIAL
@app.route('/obtenerMaterialPorTema', methods=['GET','POST'])
def obtenerListadoMaterial():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionMaterial = mongo.db.material
  
  materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})

  materiales = dumps(materiales)

  return jsonify(materiales)

@app.route('/obtenerMaterialPorId', methods=['GET','POST'])
def obtenerMaterial():
  data = request.get_json()
  
  material_id = data['material_id']

  coleccionMaterial = mongo.db.material
  
  material = coleccionMaterial.find_one({'_id':ObjectId(material_id)})
  
  material = dumps(material)
  
  return jsonify(material)

@app.route('/ingresarMaterial', methods=['GET','POST'])
def ingresarMaterial():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  texto = data['texto']
  documento = data['documento']
  video = data['video']
  imagen = data['imagen'],
  quiz = data['quiz'],
  ejemplos = data['ejemplos']
  importancia = data['importancia']

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
    'importancia': importancia
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
                'importancia': importancia
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

# SESIÓN
@app.route('/iniciarSesionAlumno', methods=['GET','POST'])
def iniciarSesionAlumno():
  data = request.get_json()

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno
  alumno = coleccionAlumno.find_one({'codigo':codigo,'contrasena':contrasena})

  alumno_id = ""

  if(alumno):
    alumno_id = (str(alumno['_id']))
  
  objetoAlumno = {
    "alumno_id": alumno_id
  }

  return jsonify(objetoAlumno)

@app.route('/iniciarSesionProfesor', methods=['GET','POST'])
def iniciarSesionProfesor():
  data = request.get_json()

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor
  profesor = coleccionProfesor.find_one({'codigo':codigo,'contrasena':contrasena})

  profesor_id = ""
  
  if(profesor):
    profesor_id = (str(profesor['_id']))
  
  objetoProfesor = {
    "profesor_id": profesor_id
  }

  return jsonify(objetoProfesor)

# TEMA
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

# CUESTIONARIO

@app.route('/ingresarCuestionario', methods=['GET','POST'])
def ingresarCuestionario():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  preguntas = data['preguntas']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarioIngresado = coleccionCuestionario.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'preguntas': preguntas
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

  cuestionarios = dumps(cuestionarios)

  return jsonify(cuestionarios)

@app.route('/actualizarCuestionario', methods=['GET','POST'])
def actualizarCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  tema_id = data['tema_id']
  nombre = data['nombre']
  preguntas = data['preguntas']

  coleccionCuestionario = mongo.db.cuestionario

  resultado = coleccionCuestionario.update_one(
    {'_id':ObjectId(cuestionario_id)},
    {'$set':
              {
                'tema_id': ObjectId(tema_id),
                'nombre': nombre,
                'preguntas': preguntas
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

  
# EVALUACIÓN

@app.route('/ingresarEvaluacion', methods=['GET','POST'])
def ingresarEvaluacion():
  data = request.get_json()

  alumno_id = data['alumno_id']
  cuestionario_id = data['cuestionario_id']
  nota = int(data['nota'])

  coleccionEvaluacion = mongo.db.evaluacion

  evaluacionIngresada = coleccionEvaluacion.insert_one({
    'alumno_id': ObjectId(alumno_id),
    'cuestionario_id': ObjectId(cuestionario_id),
    'nota': nota
  }).inserted_id

  evaluacion = {
    'evaluacion_id' : str(evaluacionIngresada)
  }

  return jsonify(evaluacion)

@app.route('/obtenerEvaluacion', methods=['GET','POST'])
def obtenerEvaluacion():
  data = request.get_json()

  evaluacion_id = data['evaluacion_id']

  coleccionEvaluacion = mongo.db.evaluacion

  evaluacion = coleccionEvaluacion.find({"_id":ObjectId(evaluacion_id)})

  evaluacion = dumps(evaluacion)

  return jsonify(evaluacion)

# ESTILO APRENDIZAJE

@app.route('/actualizarEstiloAprendizaje',methods=['GET','POST'])
def actualizarEstiloAprendizaje():
  data = request.get_json()

  alumno_id = data['alumno_id']
  
  #processing: active|reflexive
  activo = int(data['procesamiento']['activo'])
  reflexivo = int(data['procesamiento']['reflexivo'])

  # perception: sensitive|intuitive
  sensible = int(data['percepcion']['sensible'])
  intuitivo = int(data['percepcion']['intuitivo'])

  #input: visual|verbal
  visual = int(data['entrada']['visual'])
  verbal = int(data['entrada']['verbal'])

  # #understanding: sequential/global
  sequencial = int(data['comprension']['sequencial'])
  _global = int(data['comprension']['_global'])

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
  existeAlumno = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})
  if(existeAlumno):
    coleccionEstiloAprendizaje.update_one(
    {'alumno_id' : ObjectId(alumno_id)},
    {
      '$set':{
      'procesamiento':{'activo': activo,'reflexivo':reflexivo},
      'percepcion':{'sensible':sensible,'intuitivo':intuitivo},
      'entrada':{'visual':visual,'verbal':verbal},
      'comprension':{'secuencial':sequencial,'global':_global}
      }
    }
    )
  else:
    coleccionEstiloAprendizaje.insert_one({
    'alumno_id' : ObjectId(alumno_id),
    'procesamiento':{'activo': activo,'reflexivo':reflexivo},
    'percepcion':{'sensible':sensible,'intuitivo':intuitivo},
    'entrada':{'visual':visual,'verbal':verbal},
    'comprension':{'secuencial':sequencial,'global':_global}
    })

  return 'Estilo de Aprendizaje Guardado'

# CRUD CONOCIMIENTO

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
    "material_id": ObjectId(material_id),
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

# CRUD CURSO

@app.route('/obtenerCursoPorProfesor', methods=['POST'])
def obtenerCursoPorProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionCurso = mongo.db.curso

  cursos = coleccionCurso.find({'profesor_id':ObjectId(profesor_id)})

  cursos = dumps(cursos)

  return jsonify(cursos)

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

# CRUD ALUMNO

@app.route('/obtenerAlumnos',methods=['GET'])
def obtenerAlumnos():
  coleccionAlumno = mongo.db.alumno

  alumno = coleccionAlumno.find()

  alumno = dumps(alumno)

  return jsonify(alumno)

@app.route('/obtenerAlumnoPorId',methods=['GET','POST'])
def obtenerAlumnoPorId():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionAlumno = mongo.db.alumno

  try:
    alumno = coleccionAlumno.find_one({'_id':ObjectId(alumno_id)})

    objetoAlumno = {
      'nombre': alumno['nombre'],
      'apellido_paterno': alumno['apellido_paterno'],
      'apellido_materno': alumno['apellido_materno'],
      'codigo': alumno['codigo']
    }
  except:
    objetoAlumno = {}

  return  jsonify(objetoAlumno)

@app.route('/ingresarAlumno',methods=['POST'])
def ingresarAlumno():
  data = request.get_json()

  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  alumnoIngresado = coleccionAlumno.insert_one({
    "nombre":nombre,
    "apellido_paterno":apellido_paterno,
    "apellido_materno":apellido_materno,
    "codigo":codigo,
    "contrasena":contrasena
  }).inserted_id

  alumno = {
    'alumno_id' : str(alumnoIngresado)
  }

  return jsonify(alumno)

@app.route('/actualizarAlumno',methods=['POST'])
def actualizarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.update_one(
    {'_id': ObjectId(alumno_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno,
                'codigo': codigo,
                'contrasena': contrasena
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarAlumno',methods=['POST'])
def eliminarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.delete_one({'_id': ObjectId(alumno_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

# CRUD PROFESOR

@app.route('/obtenerProfesores',methods=['GET'])
def obtenerProfesores():
  coleccionProfesor = mongo.db.profesor

  profesor = coleccionProfesor.find()

  profesor = dumps(profesor)

  return jsonify(profesor)

@app.route('/obtenerProfesorPorId',methods=['GET','POST'])
def obtenerProfesorPorId():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionProfesor = mongo.db.profesor

  try:
    profesor = coleccionProfesor.find_one({'_id':ObjectId(profesor_id)})

    objetoProfesor = {
      'nombre': profesor['nombre'],
      'apellido_paterno': profesor['apellido_paterno'],
      'apellido_materno': profesor['apellido_materno'],
      'codigo': profesor['codigo']
    }
  except:
    objetoProfesor = {}

  return  jsonify(objetoProfesor)

@app.route('/ingresarProfesor',methods=['POST'])
def ingresarProfesor():
  data = request.get_json()

  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  profesorIngresado = coleccionProfesor.insert_one({
    "nombre":nombre,
    "apellido_paterno":apellido_paterno,
    "apellido_materno":apellido_materno,
    "codigo":codigo,
    "contrasena":contrasena
  }).inserted_id

  profesor = {
    'profesor_id' : str(profesorIngresado)
  }

  return jsonify(profesor)

@app.route('/actualizarProfesor',methods=['POST'])
def actualizarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  resultado = coleccionProfesor.update_one(
    {'_id': ObjectId(profesor_id)},
    {'$set':  
              {
                'nombre':nombre,
                'apellido_paterno':apellido_paterno,
                'apellido_materno':apellido_materno,
                'codigo': codigo,
                'contrasena': contrasena
              }
    }
  )  

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarProfesor',methods=['POST'])
def eliminarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionProfesor = mongo.db.profesor

  resultado = coleccionProfesor.delete_one({'_id': ObjectId(profesor_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

# RESPUESTA

@app.route('/obtenerRespuestaAlumno',methods=['GET','POST'])
def obtenerRespuesta():
  data = request.get_json()
  
  alumno_id = data['alumno_id']
  consulta = data['consulta']
  tema_id = data['tema_id']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  arreglo = list(conocimiento)

  conocimientosBD = []

  for elemento in arreglo:
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas']))

  modeloRespuesta = responder(consulta, conocimientosBD,tema_id)

  material_id = coleccionConocimiento.find_one({'_id':ObjectId(modeloRespuesta.intencion)})

  coleccionMaterial = mongo.db.material
 
  #material = coleccionMaterial.find_one({'_id':ObjectId(material_id['material_id'])})

  mostrar = []

  if estiloAprendizaje['procesamiento']['activo'] > estiloAprendizaje['procesamiento']['reflexivo']:
    # procesamiento = material['quiz']
    mostrar.append('quiz')
  else:
    # procesamiento = material['ejemplos']
    mostrar.append('ejemplos')

  if estiloAprendizaje['percepcion']['sensible'] > estiloAprendizaje['percepcion']['intuitivo']:
    # percepcion = material['importancia']
    mostrar.append('importancia')
  else:
    # percepcion = material['imagen']
    mostrar.append('imagen')

  if estiloAprendizaje['entrada']['verbal'] > estiloAprendizaje['entrada']['visual']:
    # entrada = material['documento']
    mostrar.append('documento')
  else:
    # entrada = material['video']
    mostrar.append('video')

  if estiloAprendizaje['comprension']['secuencial'] > estiloAprendizaje['comprension']['global']:
    # comprension = material['texto']
    mostrar.append('texto')
    comprension = ''
  else:
    materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})
    comprension = [materiali['nombre'] for materiali in materiales]

  respuesta = {
    'conocimiento_id': str(modeloRespuesta.intencion),
    'material_id': str(material_id['material_id']),
    'respuesta': random.choice(modeloRespuesta.respuestas),
    'mostrar': mostrar,
    'global': comprension
    #'procesamiento':procesamiento,#estiloAprendizaje['procesamiento'],
    #'percepcion':percepcion,#estiloAprendizaje['percepcion'],
    #'entrada':entrada,#estiloAprendizaje['entrada'],
    #'comprension':comprension#estiloAprendizaje['comprension']
  }

  return jsonify(respuesta)

@app.route('/obtenerRespuestaProfesor',methods=['GET','POST'])
def obtenerRespuestaProfesor():
  data = request.get_json()
  
  consulta = data['consulta']
  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  arreglo = list(conocimiento)

  conocimientosBD = []
 
  for elemento in arreglo:
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas']))  
  
  modeloRespuesta = responder(consulta,conocimientosBD,tema_id)

  material = coleccionConocimiento.find_one({'_id':ObjectId(modeloRespuesta.intencion)})

  respuesta = {
    'conocimiento_id': str(modeloRespuesta.intencion),
    'material_id': str(material['material_id']),
    'respuestas': random.choice(modeloRespuesta.respuestas)
  }

  return jsonify(respuesta)


# CARGAR MODELo
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
# ENTRENAMIENTO DEL MODELO

@app.route('/entrenar',methods=['GET','POST'])
def entrenar():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  
  conocimiento = coleccionConocimiento.find({
    'tema_id' : ObjectId(tema_id)  
  })
  
  arreglo = list(conocimiento)

  conocimientosBD = []

  for elemento in arreglo:
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas']))

  score = entrenarModelo(conocimientosBD,tema_id)

  return str(score)

#entrenar()

if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: c