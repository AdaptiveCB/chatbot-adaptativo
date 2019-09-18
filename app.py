from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
from semhash import cargarModelo,entrenarModelo,responder,Conocimiento,cargarVariosModelos
import pandas as pd
import random
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
@app.route('/obtenerListadoMaterial', methods=['GET','POST'])
def obtenerListadoMaterial():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionMaterial = mongo.db.material
  
  materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})

  materiales = dumps(materiales)

  return jsonify(materiales)

@app.route('/obtenerMaterial', methods=['GET','POST'])
def obtenerMaterial():
  data = request.get_json()
  
  material_id = data['material_id']

  coleccionMaterial = mongo.db.material
  
  material = coleccionMaterial.find({'_id':ObjectId(material_id)})

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

  coleccionMaterial = mongo.db.material

  materialIngresado = coleccionMaterial.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'texto': texto,
    'documento': documento,
    'video': video,
    'imagen': imagen,
  }).inserted_id

  nuevoMaterial_id = dumps(materialIngresado)

  return jsonify(nuevoMaterial_id)

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

  coleccionMaterial = mongo.db.material

  coleccionMaterial.update_one({
    {'_id':ObjectId(material_id)},
    {'$set':
              {
                'tema_id': ObjectId(tema_id),
                'nombre': nombre,
                'texto': texto,
                'documento': documento,
                'video': video,
                'imagen': imagen
              }
    }
  })

  return 'Material Actualizado'

@app.route('/eliminarMaterial', methods=['GET','POST'])
def eliminarMaterial():
  data = request.get_json()

  material_id = data['material_id']

  coleccionMaterial = mongo.db.material

  coleccionMaterial.delete_one({'_id': ObjectId(material_id)})

  return 'Material Eliminado'

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
  preguntas = data['preguntas']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarioIngresado = coleccionCuestionario.insert_one({
    'tema_id': ObjectId(tema_id),
    'preguntas': preguntas
  }).inserted_id

  nuevoCuestionario_id = dumps(cuestionarioIngresado)

  return jsonify(nuevoCuestionario_id)

@app.route('/obtenerCuestionario', methods=['GET','POST'])
def obtenerCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionario = coleccionCuestionario.find({"_id":ObjectId(cuestionario_id)})

  cuestionario = dumps(cuestionario)

  return jsonify(cuestionario)

@app.route('/obtenerCuestionarioPorTema', methods=['POST'])
def obtenerCuestionarioPorTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarios = coleccionCuestionario.find({"tema_id":ObjectId(tema_id)})

  cuestionarios = dumps(cuestionarios)

  return jsonify(cuestionarios)
  
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
  })

  nuevaEvaluacion_id = dumps(evaluacionIngresada)

  return jsonify(nuevaEvaluacion_id)

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
  nuevoConocimiento_id = coleccionConocimiento.insert_one({
    "tema_id" : ObjectId(tema_id),
    "material_id": material_id,
    "preguntas" : preguntas,
    "respuestas" : respuestas,
  }).inserted_id
  
  nuevoConocimiento_id = dumps(nuevoConocimiento_id)

  return jsonify(nuevoConocimiento_id)

@app.route('/actualizarConocimiento',methods=['POST'])
def actualizarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']
  material_id = data['material_id']
  preguntas = data['preguntas']
  respuestas = data['respuestas']

  coleccionConocimiento = mongo.db.conocimiento

  coleccionConocimiento.update_one(
    {'_id': ObjectId(conocimiento_id)},
    {'$set':  
              {
                'material_id': material_id,
                'preguntas': preguntas,
                'respuestas': respuestas,
              }
    }
  )

  return "Conocimiento actualizado"

# @app.route('/obtenerConocimiento',methods=['GET'])
# def obtenerConocimiento():
#   coleccionConocimiento = mongo.db.conocimiento
  
#   conocimiento = coleccionConocimiento.find()
  
#   conocimiento = dumps(conocimiento)

#   return jsonify(conocimiento)

@app.route('/obtenerConocimiento',methods=['GET','POST'])
def obtenerConocimiento():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  conocimiento = dumps(conocimiento)

  return jsonify(conocimiento)


# @app.route('/ingresarConocimiento',methods=['GET','POST'])
# def ingresarConocimiento():
#   data = request.get_json()

#   profesor_id = data['profesor_id']
#   curso_id = data['curso_id']
#   pregunta =  data['pregunta']
#   respuesta =  data['respuesta']
#   pdf =  data['pdf']
#   video =  data['video']

#   coleccionConocimiento = mongo.db.conocimiento
#   nuevoConocimiento_id = coleccionConocimiento.insert_one({
#     "profesor_id" : ObjectId(profesor_id),
#     "curso_id" : ObjectId(curso_id),
#     "pregunta" : pregunta,
#     "respuesta" : respuesta,
#     "pdf" : pdf,
#     "video" : video,
#   }).inserted_id

#   nuevoConocimiento_id = dumps(nuevoConocimiento_id)

#   return jsonify(nuevoConocimiento_id)

# @app.route('/actualizarConocimiento',methods=['POST'])
# def actualizarConocimiento():
#   data = request.get_json()

#   conocimiento_id = data['conocimiento_id']
#   pregunta = data['pregunta']
#   respuesta = data['respuesta']
#   pdf = data['pdf']
#   video = data['video']

#   coleccionConocimiento = mongo.db.conocimiento

#   coleccionConocimiento.update_one(
#     {'_id': ObjectId(conocimiento_id)},
#     {'$set':  
#               {
#                 'pregunta': pregunta,
#                 'respuesta': respuesta,
#                 'pdf': pdf,
#                 'video': video
#               }
#     }
#   )  

#   return "Conocimiento actualizado"


@app.route('/eliminarConocimiento',methods=['POST'])
def eliminarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']

  coleccionConocimiento = mongo.db.conocimiento

  coleccionConocimiento.delete_one({'_id': ObjectId(conocimiento_id)})

  return 'Conocimiento Eliminado'




# CRUD CURSO

@app.route('/obtenerCursos',methods=['GET'])
def obtenerCursos():
  coleccionCurso = mongo.db.curso

  curso = coleccionCurso.find()

  curso = dumps(curso)

  return jsonify(curso)

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

  nuevoCurso_id = dumps(cursoIngresado)

  return jsonify(nuevoCurso_id)

@app.route('/obtenerCursoPorProfesor', methods=['POST'])
def obtenerCursoPorProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionCurso = mongo.db.curso

  cursos = coleccionCurso.find({'profesor_id':ObjectId(profesor_id)})

  cursos = dumps(cursos)

  return jsonify(cursos)
 
@app.route('/actualizarCurso',methods=['POST'])
def actualizarCurso():
  data = request.get_json()

  curso_id = data['curso_id']
  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  coleccionCurso.update_one(
    {'_id': ObjectId(curso_id)},
    {'$set':  
              {
                'nombre': nombre
              }
    }
  )  

  return 'Curso Actualizado'

@app.route('/eliminarCurso',methods=['POST'])
def eliminarCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionCurso = mongo.db.curso

  coleccionCurso.delete_one({'_id': ObjectId(curso_id)})

  return 'Curso Eliminado'

# CRUD ALUMNO

@app.route('/obtenerAlumnos',methods=['GET'])
def obtenerAlumnos():
  coleccionAlumno = mongo.db.alumno

  alumno = coleccionAlumno.find()

  alumno = dumps(alumno)

  return jsonify(alumno)

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

  return alumnoIngresado

@app.route('/actualizarAlumno',methods=['POST'])
def actualizarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  coleccionAlumno.update_one(
    {'_id': ObjectId(alumno_id)},
    {'$set':  
              {
                'codigo': codigo,
                'contrasena': contrasena
              }
    }
  )  

  return 'Alumno Actualizado'

@app.route('/eliminarAlumno',methods=['POST'])
def eliminarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionAlumno = mongo.db.alumno

  coleccionAlumno.delete_one({'_id': ObjectId(alumno_id)})

  return 'Alumno Eliminado'

# CRUD PROFESOR

@app.route('/obtenerProfesores',methods=['GET'])
def obtenerProfesores():
  coleccionProfesor = mongo.db.profesor

  profesor = coleccionProfesor.find()

  profesor = dumps(profesor)

  return jsonify(profesor)

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

  return profesorIngresado

@app.route('/actualizarProfesor',methods=['POST'])
def actualizarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  coleccionProfesor.update_one(
    {'_id': ObjectId(profesor_id)},
    {'$set':  
              {
                'codigo': codigo,
                'contrasena': contrasena
              }
    }
  )  

  return 'Profesor Actualizado'

@app.route('/eliminarProfesor',methods=['POST'])
def eliminarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionProfesor = mongo.db.profesor

  coleccionProfesor.delete_one({'_id': ObjectId(profesor_id)})

  return 'Profesor Eliminado'

# RESPUESTA

@app.route('/obtenerRespuesta',methods=['GET','POST'])
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
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas']))

  modeloRespuesta = responder(consulta, conocimientosBD,tema_id)

  material = coleccionConocimiento.find_one({'_id':modeloRespuesta.intencion})

  respuesta = {
    'conocimiento_id': str(modeloRespuesta.intencion),
    'material_id': material['material_id'],
    'respuesta': random.choice(modeloRespuesta.respuestas),
    'procesamiento':estiloAprendizaje['procesamiento'],
    'percepcion':estiloAprendizaje['percepcion'],
    'entrada':estiloAprendizaje['entrada'],
    'comprension':estiloAprendizaje['comprension']
  }

  return jsonify(respuesta)

@app.route('/obtenerRespuestaProfesor',methods=['GET','POST'])
def obtenerRespuestaProfesor():
  data = request.get_json()
  
  consulta = data['consulta']
  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  # coleccionMaterial = mongo.db.material
  # material = coleccionMaterial.find_one({'tema_id':ObjectId(tema_id)})

  arreglo = list(conocimiento)

  conocimientosBD = []
 
  for elemento in arreglo:
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas']))  
  
  modeloRespuesta = responder(consulta,conocimientosBD,tema_id)

  material = coleccionConocimiento.find_one({'_id':modeloRespuesta.intencion})

  respuesta = {
    'conocimiento_id': str(modeloRespuesta.intencion),
    'material_id': material['material_id'],
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

# @app.route('/obtenerRespuesta',methods=['GET','POST'])
# def obtenerRespuesta():
#   data = request.get_json()
  
#   alumno_id = data['alumno_id']
#   consulta = data['consulta']

#   coleccionConocimiento = mongo.db.conocimiento

#   baseConocimiento = coleccionConocimiento.find()

#   pregunta = limpiar(consulta)

#   preguntas = [conocimiento['pregunta'] for conocimiento in baseConocimiento]
#   documentos = [limpiar(sentencia) for sentencia in preguntas]

#   diccionario = vocabulario(documentos)
  
#   similitudes = [similitud_de_coseno(pregunta,documento,documentos,diccionario) for documento in documentos]
#   similitudes = [round(x,5) for x in similitudes]
  
#   preguntaPuntaje = preguntas[similitudes.index(max(similitudes))]
  
#   conocimiento = coleccionConocimiento.find_one({'pregunta':preguntaPuntaje})
  
#   resultados = dict(zip(documentos,similitudes))
#   resultados = [[k,v] for k,v in resultados.items()]

#   coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
#   estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

#   # processing = "active" if perfil['processing']['active'] > 5 else "reflexive"
#   # perception = "sensitive" if perfil['perception']['sensitive'] > 5 else "intuitive"
#   # _input = "visual" if perfil['input']['visual'] > 5 else "verbal"
#   # understanding = "sequential" if perfil['understanding']['sequential'] > 5 else "global"

#   respuesta = {
#     'conocimiento_id': str(conocimiento['_id']),
#     'respuesta': conocimiento['respuesta'],
#     'pdf': conocimiento['pdf'],
#     'video': conocimiento['video'],
#     'procesamiento':estiloAprendizaje['procesamiento'],
#     'percepcion':estiloAprendizaje['percepcion'],
#     'entrada':estiloAprendizaje['entrada'],
#     'comprension':estiloAprendizaje['comprension']
#   }

#   return jsonify(respuesta)

#entrenar()

if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: c