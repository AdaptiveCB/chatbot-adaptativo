import os
import re
import random
import pickle
import pyrebase
import numpy as np

from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression


firebaseConfig = {
  "apiKey": "AIzaSyCicLp-X6d2XGXTUPwb9SSfYDvsuN1N2VE",
  "authDomain": "chatbot-adaptativo.firebaseapp.com",
  "databaseURL": "https://chatbot-adaptativo.firebaseio.com",
  "projectId": "chatbot-adaptativo",
  "storageBucket": "chatbot-adaptativo.appspot.com",
  "messagingSenderId": "943322485233",
  "appId": "1:943322485233:web:4d843654a0500f810bb450"
}
firebase = pyrebase.initialize_app(firebaseConfig)
FirebaseStorage = firebase.storage()

# Subir
# FirebaseStorage.child("images/new.jpg").put("foto_prueba.jpg")

# Descargar
# FirebaseStorage.child("images/new.jpg").download("example.jpg")

# Obtener Link
# print(FirebaseStorage.child("images/new.jpg").get_url(None))



modelos = {}
vectorizers = {}

class Conocimiento:
  def __init__(self, intencion, preguntas, respuestas):
    self.intencion = intencion
    self.preguntas = preguntas
    self.respuestas = respuestas

  
  def __getitem__(self):#,intencion, preguntas, respuestas):
    return [self.intencion,self.preguntas,self.respuestas]

def tratamiento(text):
  text = text.lower()
#   text = re.sub(r'[^a-zá-úñÑ¿?\s]+', ' ', text)#   
  text = re.sub(r'[^a-zá-úñÑ\s]+', ' ', text)
  text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
  text = text.split()
  return ' '.join(text)

def ngrams(text, n):
  ngrams = zip(*[text[i:] for i in range(n)])
  ngrams = [''.join(ng) for ng in ngrams]
  return ngrams

def semhash(text, n):
  text = tratamiento(text)
  tokens = []
  for t in text.split():
    t = '#{}#'.format(t)
    tokens += ngrams(t, n)
  return ' '.join(tokens)

n = 3 #tamaño n-gram
intenciones = []

def entrenarModelo(conocimientos,tema_id):
  vectorizer = CountVectorizer(token_pattern='[#a-zñ0-9]+')
  intenciones = [c.intencion for c in conocimientos]
  # for c in conocimientos:
  #   print(c.intencion, c.preguntas, c.respuestas)
  x_train = []
  y_train = []
  
  for c in conocimientos:
    x_train.extend([m for m in c.preguntas])
    y_train.extend([intenciones.index(c.intencion)]*len(c.preguntas))

  x_train_semhash = [semhash(x, n) for x in x_train]
  vectorizer.fit(x_train_semhash)
  x_train_vector = vectorizer.transform(x_train_semhash).toarray()

  model = LogisticRegression(C=1.0, class_weight=None, dual=False,
          fit_intercept=True, intercept_scaling=1, max_iter=100,
          multi_class='ovr', n_jobs=1, penalty='l2', random_state=None,
          solver='liblinear', tol=0.0001, verbose=0, warm_start=False)
  model.fit(x_train_vector, y_train)
  
  predicciones = model.predict(x_train_vector)
  score = metrics.accuracy_score(y_train, predicciones)

  modelos.update({tema_id:model})
  vectorizers.update({tema_id:vectorizer})
  
  filename = os.path.join('models',tema_id+'.sav')
  pickle.dump(model, open(filename, 'wb'))
  FirebaseStorage.child('models',tema_id+'.sav').put(os.path.join('models',tema_id+'.sav'))

  filenameVectorizer = os.path.join('vectorizer',tema_id+'.sav')
  pickle.dump(vectorizer, open(filenameVectorizer, 'wb'))
  FirebaseStorage.child('vectorizer',tema_id+'.sav').put(os.path.join('vectorizer',tema_id+'.sav'))
  
  return score

def cargarModelo(tema_id):
  FirebaseStorage.child('models',tema_id+'.sav').download(os.path.join('models',tema_id+'.sav'))
  FirebaseStorage.child('vectorizer',tema_id+'.sav').download(os.path.join('vectorizer',tema_id+'.sav'))
  filename = os.path.join('models',tema_id+'.sav')
  model = pickle.load(open(filename, 'rb'))

  filenameVectorizer = os.path.join('vectorizer',tema_id+'.sav')
  vectorizer = pickle.load(open(filenameVectorizer, 'rb'))

  modelos.update({tema_id:model})  
  vectorizers.update({tema_id:vectorizer})

def cargarVariosModelos(temas):
  for tema_id in temas:
    FirebaseStorage.child('models',tema_id+'.sav').download(os.path.join('models',tema_id+'.sav'))
    FirebaseStorage.child('vectorizer',tema_id+'.sav').download(os.path.join('vectorizer',tema_id+'.sav'))
    filename = os.path.join('models',tema_id+'.sav')
    filenameVectorizer = os.path.join('vectorizer',tema_id+'.sav')
    if(os.path.exists(filename)):
      model = pickle.load(open(filename, 'rb'))
      modelos.update({tema_id:model})  
      vectorizer = pickle.load(open(filenameVectorizer, 'rb'))
      vectorizers.update({tema_id:vectorizer})

def responder(pregunta,conocimientos,tema_id):
  cargarModelo(tema_id)

  vectorizer = vectorizers.get(tema_id)

  model = modelos.get(tema_id)

  x_semhash = [semhash(pregunta, n)]
  
  x_vector = vectorizer.transform(x_semhash).toarray()

  probabilidades = model.predict_proba(x_vector)[0]

  idx = np.argmax(probabilidades)

  return conocimientos[idx]
  
 