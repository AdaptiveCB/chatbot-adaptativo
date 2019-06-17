from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno
import pandas as pd

app = Flask(__name__)

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
  codigo = request.form['codigo']
  #processing: active|reflexive
  active = int(request.form['procesamiento'])
  reflexive = 11-active
  #perception: sensitive|intuitive
  sensitive = int(request.form['percepcion'])
  intuitive = 11-sensitive
  #input: visual|verbal
  visual = int(request.form['entrada'])
  verbal = 11-visual
  #understanding: sequential/global
  sequential = int(request.form['comprension'])
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

@app.route('/pregunta',methods=['GET','POST'])
def pregunta():
  pregunta = request.form['consulta']
  print(pregunta)
  #pregunta = consulta
  pregunta = limpiar(pregunta)

  preguntas = mongo.db.questions
  preguntas = preguntas.find({})
  preguntas = [pregunta['question'] for pregunta in preguntas]
  documentos = [limpiar(sentencia) for sentencia in preguntas]

  diccionario = vocabulario(documentos)
  
  similitudes = [similitud_de_coseno(pregunta,documento,documentos,diccionario) for documento in documentos]
  similitudes = [round(x,5) for x in similitudes]
  # print('maximo: ', max(similitudes))
  preguntaPuntaje = preguntas[similitudes.index(max(similitudes))]
  respuestas = mongo.db.answers
  respuesta = respuestas.find_one({'question':preguntaPuntaje})
  # respuesta = respuesta['answer']
  
  resultados = dict(zip(documentos,similitudes))
  resultados = [[k,v] for k,v in resultados.items()]

  respuesta = {
    'answer': respuesta['answer'],
    'test': respuesta['test'],
    'reading': respuesta['reading'],
    'application': respuesta['application'],
    'text': respuesta['text'],
    'video': respuesta['video'],
    'podcast': respuesta['podcast'],
    'prezi': respuesta['prezi'],
    'model': respuesta['model']
  }

  # print(respuesta)
  
  return jsonify(respuesta)
  #return render_template('pregunta.html', resultados = resultados, respuesta = respuesta)

if __name__ == '__main__':
  app.run(debug=True)



# deploy heroku: https://www.youtube.com/watch?v=pmRT8QQLIqk