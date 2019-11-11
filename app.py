from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
from semhash import cargarModelo,entrenarModelo,responder,Conocimiento,Entidad,cargarVariosModelos
import pandas as pd
import random
import re

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
  imagen = data['imagen']
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
  importancia = data['importancia']
  faq = data['faq']

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

# procesamiento
# activo/reflexivo

# percepcion
# sensorial/intuitivo

# entrada
# visual/verbal

# comprension
# secuencial/global

@app.route('/obtenerEstiloAprendizajePorAlumnoId', methods=['POST'])
def obtenerEstiloAprendizajePorAlumnoId():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  estilos = {
    'alumno_id': alumno_id,
    'procesamiento': estiloAprendizaje['procesamiento']['categoria'],
    'procesamiento_valor': estiloAprendizaje['procesamiento']['valor'],
    'percepcion': estiloAprendizaje['percepcion']['categoria'],
    'percepcion_valor': estiloAprendizaje['percepcion']['valor'],
    'entrada': estiloAprendizaje['entrada']['categoria'],
    'entrada_valor': estiloAprendizaje['entrada']['valor'],
    'comprension': estiloAprendizaje['comprension']['categoria'],
    'comprension_valor': estiloAprendizaje['comprension']['valor']
  }

  return jsonify(estilos)


@app.route('/actualizarEstiloAprendizaje',methods=['POST'])
def actualizarEstiloAprendizaje():
  data = request.get_json()

  alumno_id = data['alumno_id']

  procesamiento_valor = data['procesamiento_valor']
  percepcion_valor = data['percepcion_valor']
  entrada_valor = data['entrada_valor']
  comprension_valor = data['comprension_valor']

  procesamiento_categoria = data['procesamiento']
  percepcion_categoria = data['percepcion']
  entrada_categoria = data['entrada']
  comprension_categoria = data['comprension']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
  existeAlumno = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  if(existeAlumno):
    resultado = coleccionEstiloAprendizaje.update_one(
      {'alumno_id' : ObjectId(alumno_id)},
      {
        '$set':{
        'procesamiento':{'categoria': procesamiento_categoria,'valor': procesamiento_valor},
        'percepcion':{'categoria': percepcion_categoria,'valor': percepcion_valor},
        'entrada':{'categoria': entrada_categoria,'valor': entrada_valor},
        'comprension':{'categoria': comprension_categoria,'valor': comprension_valor}
        }
      }
    )

    respuesta = {
      'encontrado': resultado.matched_count,
      'modificado': resultado.modified_count
    }

  else:
    estiloAprendizajeIngresado = coleccionEstiloAprendizaje.insert_one(
      {
        'alumno_id' : ObjectId(alumno_id),
        'procesamiento':{'categoria': procesamiento_categoria,'valor': procesamiento_valor},
        'percepcion':{'categoria': percepcion_categoria,'valor': percepcion_valor},
        'entrada':{'categoria': entrada_categoria,'valor': entrada_valor},
        'comprension':{'categoria': comprension_categoria,'valor': comprension_valor}
      }
    ).inserted_id

    respuesta = {
      'estiloAprendizaje_id' : str(estiloAprendizajeIngresado)
    }

  return jsonify(respuesta)

# @app.route('/actualizarEstiloAprendizaje',methods=['GET','POST'])
# def actualizarEstiloAprendizaje():
#   data = request.get_json()

#   alumno_id = data['alumno_id']
  
#   #processing: active|reflexive
#   activo = int(data['procesamiento']['activo'])
#   reflexivo = int(data['procesamiento']['reflexivo'])

#   # perception: sensitive|intuitive
#   sensible = int(data['percepcion']['sensible'])
#   intuitivo = int(data['percepcion']['intuitivo'])

#   #input: visual|verbal
#   visual = int(data['entrada']['visual'])
#   verbal = int(data['entrada']['verbal'])

#   # #understanding: sequential/global
#   sequencial = int(data['comprension']['sequencial'])
#   _global = int(data['comprension']['_global'])

#   coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
#   existeAlumno = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})
#   if(existeAlumno):
#     coleccionEstiloAprendizaje.update_one(
#     {'alumno_id' : ObjectId(alumno_id)},
#     {
#       '$set':{
#       'procesamiento':{'activo': activo,'reflexivo':reflexivo},
#       'percepcion':{'sensible':sensible,'intuitivo':intuitivo},
#       'entrada':{'visual':visual,'verbal':verbal},
#       'comprension':{'secuencial':sequencial,'global':_global}
#       }
#     }
#     )
#   else:
#     coleccionEstiloAprendizaje.insert_one({
#     'alumno_id' : ObjectId(alumno_id),
#     'procesamiento':{'activo': activo,'reflexivo':reflexivo},
#     'percepcion':{'sensible':sensible,'intuitivo':intuitivo},
#     'entrada':{'visual':visual,'verbal':verbal},
#     'comprension':{'secuencial':sequencial,'global':_global}
#     })

#   return 'Estilo de Aprendizaje Guardado'

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

# CRUD CURSO

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

# CRUD ENTIDAD

@app.route('/obtenerEntidadPorTema', methods=['GET','POST'])
def obtenerEntidadPorTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionEntidad = mongo.db.entidad
  
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})

  entidades = dumps(entidades)

  return jsonify(entidades)

@app.route('/ingresarEntidad',methods=['POST'])
def ingresarEntidad():
  data = request.get_json()

  nombre = data['nombre']
  columnas = data['columnas']
  datos = data['datos']
  tema_id = data['tema_id']

  coleccionEntidad = mongo.db.entidad

  entidadIngresada = coleccionEntidad.insert_one({
    'nombre':nombre,
    'columnas':columnas,
    'datos':datos,
    'tema_id':ObjectId(tema_id)
  }).inserted_id

  entidad = {
    'entidad_id' : str(entidadIngresada)
  }

  return jsonify(entidad)

@app.route('/actualizarEntidad',methods=['POST'])
def actualizarEntidad():
  data = request.get_json()

  entidad_id = data['entidad_id']
  nombre = data['nombre']
  columnas = data['columnas']
  datos = data['datos']
  # tema_id = data['tema_id']
  
  coleccionEntidad = mongo.db.entidad

  resultado = coleccionEntidad.update_one(
    {'_id': ObjectId(entidad_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'columnas':columnas,
                'datos':datos,
                # 'tema_id': ObjectId(tema_id)
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarEntidad',methods=['POST'])
def eliminarEntidad():
  data = request.get_json()

  entidad_id = data['entidad_id']

  coleccionEntidad = mongo.db.entidad

  resultado = coleccionEntidad.delete_one({'_id': ObjectId(entidad_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

# CRUD ALUMNO

@app.route('/obtenerAlumnosPorCurso', methods=['POST'])
def obtenerAlumnosPorCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula

  alumnos = coleccionMatricula.find({'curso_id':ObjectId(curso_id)})

  alumnos = [str(alumno['alumno_id']) for alumno in alumnos]

  alumnos = {
    'alumnos':alumnos
  }

  return jsonify(alumnos)

@app.route('/matricularAlumno', methods=['POST'])
def matricularAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula
  
  matriculaExiste = coleccionMatricula.find_one({
    '$and':[
      {'alumno_id': ObjectId(alumno_id)},
      {'curso_id': ObjectId(curso_id)}
    ]
  })

  if not matriculaExiste:
    matriculaNueva = coleccionMatricula.insert_one({
      'alumno_id': ObjectId(alumno_id),
      'curso_id': ObjectId(curso_id)
    }).inserted_id

    matricula = {
      'matricula_id' : str(matriculaNueva)
    }
  else:
    matricula = {
      'respuesta' : 'matricula ya existe'
    }

  return jsonify(matricula)

@app.route('/desmatricularAlumno', methods=['POST'])
def desmatricularAlumno():
  data = request.get_json() 

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula

  resultado = coleccionMatricula.delete_one({'alumno_id': ObjectId(alumno_id),'curso_id': ObjectId(curso_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)


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
      'alumno_id': alumno_id,
      'nombre': alumno['nombre'],
      'apellido_paterno': alumno['apellido_paterno'],
      'apellido_materno': alumno['apellido_materno'],
      'codigo': alumno['codigo']
    }
  except:
    objetoAlumno = {}

  return  jsonify(objetoAlumno)

@app.route('/obtenerAlumnoPorNombre',methods=['POST'])
def obtenerAlumnoPorNombre():
  data = request.get_json()

  alumno_nombre = data['alumno_nombre']

  coleccionAlumno = mongo.db.alumno

  alumnos = coleccionAlumno.find({
    '$or':[
      {'nombre':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}},
      {'apellido_paterno':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}},
      {'apellido_materno':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}}
    ]
  })

  alumnos = dumps(alumnos)

  return jsonify(alumnos)

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

@app.route('/actualizarContrasenaAlumno',methods=['POST'])
def actualizarContrasenaAlumno():
  data = request.get_json()
  
  alumno_id = data['alumno_id']
  contrasena_actual = data['contrasena_actual']
  contrasena_nueva = data['contrasena_nueva']

  coleccionAlumno = mongo.db.alumno

  alumno = coleccionAlumno.find_one({'_id' : ObjectId(alumno_id)})

  if contrasena_actual == alumno['contrasena']:
    resultado = coleccionAlumno.update_one(
      {'_id': ObjectId(alumno_id)},
      {'$set':  
                {
                  'contrasena': contrasena_nueva
                }
      }
    )  

    objetoResultado = {
      'encontrado': resultado.matched_count,
      'modificado': resultado.modified_count
    }
  
  else:
    objetoResultado = {
      'respuestas': 'contrasena actual incorrecta'
    }

  return jsonify(objetoResultado)

@app.route('/actualizarAlumno',methods=['POST'])
def actualizarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  #codigo = data['codigo']
  #contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.update_one(
    {'_id': ObjectId(alumno_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno
                #'codigo': codigo,
                #'contrasena': contrasena
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
      'profesor_id': profesor_id,
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

@app.route('/actualizarContrasenaProfesor',methods=['POST'])
def actualizarContrasenaProfesor():
  data = request.get_json()
  
  profesor_id = data['profesor_id']
  contrasena_actual = data['contrasena_actual']
  contrasena_nueva = data['contrasena_nueva']

  coleccionProfesor = mongo.db.profesor

  profesor = coleccionProfesor.find_one({'_id' : ObjectId(profesor_id)})

  if contrasena_actual == profesor['contrasena']:
    resultado = coleccionProfesor.update_one(
      {'_id': ObjectId(profesor_id)},
      {'$set':  
                {
                  'contrasena': contrasena_nueva
                }
      }
    )  

    objetoResultado = {
      'encontrado': resultado.matched_count,
      'modificado': resultado.modified_count
    }
  
  else:
    objetoResultado = {
      'respuestas': 'contrasena actual incorrecta'
    }

  return jsonify(objetoResultado)

@app.route('/actualizarProfesor',methods=['POST'])
def actualizarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  #codigo = data['codigo']
  #contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  resultado = coleccionProfesor.update_one(
    {'_id': ObjectId(profesor_id)},
    {'$set':  
              {
                'nombre':nombre,
                'apellido_paterno':apellido_paterno,
                'apellido_materno':apellido_materno
                #'codigo': codigo,
                #'contrasena': contrasena
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

# @app.route('/obtenerRespuestaAlumno',methods=['GET','POST'])
# def obtenerRespuesta():
  # data = request.get_json()
  
  # alumno_id = data['alumno_id']
  # consulta = data['consulta']
  # tema_id = data['tema_id']

  # coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  # estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  # coleccionConocimiento = mongo.db.conocimiento
  # conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  # arreglo = list(conocimiento)

  # conocimientosBD = []

  # for elemento in arreglo:
  #   conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas']))

  # modeloRespuesta = responder(consulta, conocimientosBD,tema_id)

  # material_id = coleccionConocimiento.find_one({'_id':ObjectId(modeloRespuesta.conocimiento_id)})

  # coleccionMaterial = mongo.db.material
 
  # material = coleccionMaterial.find_one({'_id':ObjectId(material_id['material_id'])})

  # mostrar = []

  # if estiloAprendizaje['procesamiento']['activo'] > estiloAprendizaje['procesamiento']['reflexivo']:
  #   # procesamiento = material['quiz']
  #   mostrar.append('quiz')
  # else:
  #   # procesamiento = material['ejemplos']
  #   mostrar.append('ejemplos')

  # if estiloAprendizaje['percepcion']['sensible'] > estiloAprendizaje['percepcion']['intuitivo']:
  #   # percepcion = material['importancia']
  #   mostrar.append('importancia')
  # else:
  #   # percepcion = material['imagen']
  #   mostrar.append('imagen')

  # if estiloAprendizaje['entrada']['verbal'] > estiloAprendizaje['entrada']['visual']:
  #   # entrada = material['documento']
  #   mostrar.append('documento')
  # else:
  #   # entrada = material['video']
  #   mostrar.append('video')

  # if estiloAprendizaje['comprension']['secuencial'] > estiloAprendizaje['comprension']['global']:
  #   # comprension = material['texto']
  #   mostrar.append('texto')
  #   comprension = ''
  # else:
  #   materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})
  #   comprension = [materiali['nombre'] for materiali in materiales]

  # respuesta = {
  #   'conocimiento_id': str(modeloRespuesta.conocimiento_id),
  #   'material_id': str(material_id['material_id']),
  #   'respuesta': random.choice(modeloRespuesta.respuestas),
  #   'mostrar': mostrar,
  #   'global': comprension
    #'procesamiento':procesamiento,#estiloAprendizaje['procesamiento'],
    #'percepcion':percepcion,#estiloAprendizaje['percepcion'],
    #'entrada':entrada,#estiloAprendizaje['entrada'],
    #'comprension':comprension#estiloAprendizaje['comprension']
  # }

  # if comprension == '':
  #   respuesta.pop('global')

  # return jsonify(respuesta)

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
  entidadBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   
  
  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, alumno)
  
  if material_id != '':
    coleccionMaterial = mongo.db.material
    material = coleccionMaterial.find_one({'_id':material_id})
    
    if estiloAprendizaje['procesamiento']['valor']<=3 :
      activo=1
      reflexivo=1
    else:
      if estiloAprendizaje['procesamiento']['categoria']=='activo' :
        activo=1
        reflexivo=0
      else:
        activo=0
        reflexivo=1
    
    if estiloAprendizaje['percepcion']['valor']<=3 :
      sensorial=1
      intuitivo=1
    else:
      if estiloAprendizaje['percepcion']['categoria']=='intuitivo' :
        sensorial=0
        intuitivo=1
      else:
        sensorial=1
        intuitivo=0
    
    if estiloAprendizaje['entrada']['valor']<=3 :
      verbal=1
      visual=1
    else:
      if estiloAprendizaje['entrada']['categoria']=='visual' :
        verbal=0
        visual=1
      else:
        verbal=1
        visual=0

    if estiloAprendizaje['comprension']['valor']<=3 :
      secuencial=1
      _global=1
    else:
      if estiloAprendizaje['comprension']['categoria']=='secuencial' :
        secuencial=1
        _global=0
      else:
        secuencial=0
        _global=1

    recursos = []
    recursosD = {}
    
    if(sensorial or secuencial or _global):
      recursosD['texto']=material['texto']

    if(intuitivo or verbal or reflexivo or secuencial):
      recursosD['importancia']=material['importancia']

    if(intuitivo or _global):
      recursosD['explicacion']=material['explicacion']

    if(sensorial or activo or secuencial):
      recursosD['ejemplos']=material['ejemplos']

    if(activo or secuencial):
      recursosD['quiz']=material['quiz']

    if(intuitivo or visual):
      recursosD['imagen']=material['imagen']

    if(verbal):
      recursosD['documento']=material['documento']
      
    if(visual):
      recursosD['video']=material['video']

    if(sensorial or verbal or activo):
      recursosD['faq']=material['faq']

  else:
    recursosD = {}

  respuesta = {
    'respuesta': respuesta,
    'material_id': str(material_id),
    'datos_ingresados': datos_ingresados,
    'datos_faltantes': datos_faltantes,
    'success': success,
    'recursos': recursosD
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
  entidadBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   
  
  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, profesor)
  
  respuesta = {
    'respuesta': respuesta,
    'material_id': str(material_id),
    'datos_ingresados': datos_ingresados,
    'datos_faltantes': datos_faltantes,
    'success': success
  }

  return jsonify(respuesta)


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
# ENTRENAMIENTO DEL MODELO

@app.route('/entrenar',methods=['GET','POST'])
def entrenar():
  data = request.get_json()
  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({
    'tema_id' : ObjectId(tema_id)  
  })
  
  conocimientosBD = []
  for elemento in list(conocimiento):
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas'],elemento['material_id']))

  score = entrenarModelo(conocimientosBD,tema_id)

  return str(score)

#entrenar()

if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: c