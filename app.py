from flask import Flask, render_template, request
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

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/pregunta',methods=['POST'])
def pregunta():
  pregunta = request.form['consulta']
  # queries = mongo.db.queries
  # queries.insert({'query':pregunta})
  questions = mongo.db.questions
  print(questions)
  preguntas = questions.find({})
  print(preguntas)
  preguntas = [pregunta['question'] for pregunta in preguntas]
  documentos = [limpiar(sentencia) for sentencia in preguntas]
  diccionario = vocabulario(documentos)
  celdas = [similitud_de_coseno(pregunta,documento,documentos,diccionario) for documento in documentos]
  tabla = pd.DataFrame(celdas,documentos,['Similitud de cosenos'])
  print(documentos)
  print(diccionario)
  print(documento_a_vector('qué es una clase',diccionario))
  print(celdas)
  print(tabla)
  resultados = dict(zip(documentos,celdas))
  print('------------')
  print(resultados)
  print('------------')
  
  final = [[k,v] for k,v in resultados.items()]
  print(final)
  
  return render_template('pregunta.html', resultados = final)

if __name__ == '__main__':
  app.run(debug=True)