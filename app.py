from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
import pandas as pd

app = Flask(__name__)

CORS(app)

app.config['MONGO_DBNAME'] = 'chatbot'
app.config['MONGO_URI'] = 'mongodb+srv://chatbot:adaptive@cluster0-k4fnb.mongodb.net/chatbot?retryWrites=true&w=majority'#'mongodb://localhost/chatbot'

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
  active = int(data['procesamiento'])
  reflexive = 11-active
  #perception: sensitive|intuitive
  sensitive = int(data['percepcion'])
  intuitive = 11-sensitive
  #input: visual|verbal
  visual = int(data['entrada'])
  verbal = 11-visual
  #understanding: sequential/global
  sequential = int(data['comprension'])
  _global = 11-sequential
  
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

# @app.route('/prueba', methods=['GET','POST'])
# def prueba():
#   data = request.get_json()
#   print(data['codigo'])
#   print(data['pregunta'])

#   return 'prueba'


@app.route('/pregunta',methods=['GET','POST'])
def pregunta():
  # pregunta = request.form['consulta']
  # codigo = request.form['codigo']
  data = request.get_json()
  pregunta = data['consulta']
  codigo = data['codigo']
  # print(pregunta)
  #pregunta = consulta
  pregunta = limpiar(pregunta)

  preguntas = mongo.db.questions
  preguntas = preguntas.find({})
  preguntas = [pregunta['question'] for pregunta in preguntas]
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
  #return render_template('pregunta.html', resultados = resultados, respuesta = respuesta)

if __name__ == '__main__':
  app.run(debug=True)


# url app: https://adaptive-chatbot.herokuapp.com/
# deploy heroku: https://www.youtube.com/watch?v=pmRT8QQLIqk