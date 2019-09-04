import re
import random

from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class Conocimiento:
  def __init__(self, intencion, preguntas, respuestas,pdf="",video=""):
    self.intencion = intencion
    self.preguntas = preguntas
    self.respuestas = respuestas
    self.pdf = pdf
    self.video = video

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
vectorizer = CountVectorizer(token_pattern='[#a-zñ0-9]+')
intenciones = []

def entrenarModelo(conocimientos):
  global intenciones, model
  intenciones = [c.intencion for c in conocimientos]
  for c in conocimientos:
    print(c.intencion, c.preguntas, c.respuestas)
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
  
  return score


def responder(pregunta):
  x_semhash = [semhash(pregunta, n)]
  x_vector = vectorizer.transform(x_semhash).toarray()
  prediccion = model.predict(x_vector)[0]
  intencion = intenciones[prediccion]

  respuesta = ""
  pdf = ""
  video = ""
  conocimiento_id = ""
  for c in conocimientos:

    if c.intencion == intencion:
      conocimiento_id = c.intencion
      respuesta = random.choice(c.respuestas)
      pdf = c.pdf
      video = c.video
      break
  objeto = {
    'conocimiento_id':conocimiento_id,
    'respuesta':respuesta,
    'pdf':pdf,
    'video':video
  }
  return objeto