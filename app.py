from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
import pandas as pd
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

# ESTILO APRENDIZAJE

@app.route('/actualizarEstiloAprendizaje',methods=['GET','POST'])
def perfil():
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

@app.route('/obtenerConocimiento',methods=['GET'])
def obtenerConocimiento():
  coleccionConocimiento = mongo.db.conocimiento
  
  conocimiento = coleccionConocimiento.find()
  
  conocimiento = dumps(conocimiento)

  return jsonify(conocimiento)


@app.route('/ingresarConocimiento',methods=['GET','POST'])
def ingresarConocimiento():
  data = request.get_json()

  profesor_id = data['profesor_id']
  curso_id = data['curso_id']
  pregunta =  data['pregunta']
  respuesta =  data['respuesta']
  pdf =  data['pdf']
  video =  data['video']

  coleccionConocimiento = mongo.db.conocimiento
  coleccionConocimiento.insert_one({
    "profesor_id" : ObjectId(profesor_id),
    "curso_id" : ObjectId(curso_id),
    "pregunta" : pregunta,
    "respuesta" : respuesta,
    "pdf" : pdf,
    "video" : video,
  })

  return "Conocimiento guardado"


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

  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  coleccionCurso.insert_one({"nombre":nombre})

  return 'Curso Ingresado'

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

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  coleccionAlumno.insert_one({"codigo":codigo,"contrasena":contrasena})

  return 'Alumno Ingresado'

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

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  coleccionProfesor.insert_one({"codigo":codigo,"contrasena":contrasena})

  return 'Profesor Ingresado'

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
def pregunta():
  data = request.get_json()
  
  alumno_id = data['alumno_id']
  consulta = data['consulta']

  coleccionConocimiento = mongo.db.conocimiento

  baseConocimiento = coleccionConocimiento.find()

  pregunta = limpiar(consulta)

  preguntas = [conocimiento['pregunta'] for conocimiento in baseConocimiento]
  documentos = [limpiar(sentencia) for sentencia in preguntas]

  diccionario = vocabulario(documentos)
  
  similitudes = [similitud_de_coseno(pregunta,documento,documentos,diccionario) for documento in documentos]
  similitudes = [round(x,5) for x in similitudes]
  
  preguntaPuntaje = preguntas[similitudes.index(max(similitudes))]
  
  conocimiento = coleccionConocimiento.find_one({'pregunta':preguntaPuntaje})
  
  resultados = dict(zip(documentos,similitudes))
  resultados = [[k,v] for k,v in resultados.items()]

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  # processing = "active" if perfil['processing']['active'] > 5 else "reflexive"
  # perception = "sensitive" if perfil['perception']['sensitive'] > 5 else "intuitive"
  # _input = "visual" if perfil['input']['visual'] > 5 else "verbal"
  # understanding = "sequential" if perfil['understanding']['sequential'] > 5 else "global"

  respuesta = {
    'conocimiento_id': str(conocimiento['_id']),
    'respuesta': conocimiento['respuesta'],
    'pdf': conocimiento['pdf'],
    'video': conocimiento['video'],
    'procesamiento':estiloAprendizaje['procesamiento'],
    'percepcion':estiloAprendizaje['percepcion'],
    'entrada':estiloAprendizaje['entrada'],
    'comprension':estiloAprendizaje['comprension']
  }

  return jsonify(respuesta)

  
if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: c