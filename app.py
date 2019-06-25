from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
import pandas as pd
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

@app.route('/perfil',methods=['GET','POST'])
def perfil():
  data = request.get_json()
  # codigo = request.form['codigo']
  codigo = data['codigo']
  #processing: active|reflexive

  active = int(data['processing']['active'])
  reflexive = int(data['processing']['reflexive'])
  # perception: sensitive|intuitive
  sensitive = int(data['perception']['sensitive'])
  intuitive = int(data['perception']['intuitive'])
  # #input: visual|verbal
  visual = int(data['input']['visual'])
  verbal = int(data['input']['verbal'])
  # #understanding: sequential/global
  sequential = int(data['understanding']['sequential'])
  _global = int(data['understanding']['_global'])
  
  perfiles = mongo.db.learningprofiles
  
  perfiles.update_one(
    {'codigo' : codigo},
    {
      '$set':{
      'processing':{'active': active,'reflexive':reflexive},
      'perception':{'sensitive':sensitive,'intuitive':intuitive},
      'input':{'visual':visual,'verbal':verbal},
      'understanding':{'sequential':sequential,'global':_global}
      }
    }
  )

  return 'Guardado'

@app.route('/preguntas',methods=['GET'])
def preguntas():
  respuestas = mongo.db.answers
  respuestas = dumps(respuestas.find())

  # in default raise TypeError(f'Object of type {o.__class__.__name__} '
  #  Object of type ObjectId is not JSON serializable
  print(respuestas)
  return jsonify(respuestas)
  # preguntas = [respuesta['question'] for respuesta in respuestas]
  # documentos = [limpiar(sentencia) for sentencia in preguntas]


@app.route('/respuesta',methods=['GET','POST'])
def respuesta():
  data = request.get_json()

  answer =  data['answer']
  question =  data['question']
  test =  data['test']
  reading =  data['reading']
  application =  data['application']
  text =  data['text']
  video =  data['video']
  podcast =  data['podcast']
  prezi =  data['prezi']
  model =  data['model']

  # questions = mongo.db.questions
  # questions.insert_one({'question':question})

  answers = mongo.db.answers
  answers.insert_one({
    "answer" :  answer,
    "question" :  question,
    "test" :  test,
    "reading" :  reading,
    "application" :  application,
    "text" :  text,
    "video" :  video,
    "podcast" :  podcast,
    "prezi" :  prezi,
    "model" :  model
  })

  return "Respuesta guardada"

@app.route('/pregunta',methods=['GET','POST'])
def pregunta():
  data = request.get_json()
  pregunta = data['consulta']
  codigo = data['codigo']

  pregunta = limpiar(pregunta)

  respuestas = mongo.db.answers
  respuestas = respuestas.find({})
  preguntas = [respuesta['question'] for respuesta in respuestas]
  documentos = [limpiar(sentencia) for sentencia in preguntas]

  diccionario = vocabulario(documentos)
  
  similitudes = [similitud_de_coseno(pregunta,documento,documentos,diccionario) for documento in documentos]
  similitudes = [round(x,5) for x in similitudes]
  
  preguntaPuntaje = preguntas[similitudes.index(max(similitudes))]
  
  respuestas = mongo.db.answers
  respuesta = respuestas.find_one({'question':preguntaPuntaje})
  
  resultados = dict(zip(documentos,similitudes))
  resultados = [[k,v] for k,v in resultados.items()]

  perfiles = mongo.db.learningprofiles
  perfil = perfiles.find_one({'codigo' : codigo})

  processing = "active" if perfil['processing']['active'] > 5 else "reflexive"
  perception = "sensitive" if perfil['perception']['sensitive'] > 5 else "intuitive"
  _input = "visual" if perfil['input']['visual'] > 5 else "verbal"
  understanding = "sequential" if perfil['understanding']['sequential'] > 5 else "global"

  respuesta = {
    'id': str(respuesta['_id']),
    'answer': respuesta['answer'],
    'test': respuesta['test'],
    'reading': respuesta['reading'],
    'application': respuesta['application'],
    'text': respuesta['text'],
    'video': respuesta['video'],
    'podcast': respuesta['podcast'],
    'prezi': respuesta['prezi'],
    'model': respuesta['model'],
    'processing':processing,
    'perception':perception,
    'input':_input,
    'understanding':understanding
  }

  return jsonify(respuesta)

# @app.route('/prueba',methods=['GET','POST'])
# def prueba():
#   respuestas = mongo.db.answers
#   respuesta = respuestas.find_one({"respuesta":"tarde"})
#   objeto = {
#     'id': str(respuesta['_id']),
#     'answer': respuesta['respuesta'],
#     'question': respuesta['pregunta']
#   }
#   print(objeto)
#   return "OK"

if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: c