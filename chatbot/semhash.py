import os
import re
import random
import pickle
import pyrebase
import numpy as np
from collections import defaultdict

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
  def __init__(self, conocimiento_id, preguntas, respuestas, material_id):
    self.conocimiento_id = conocimiento_id
    self.preguntas = preguntas
    self.respuestas = respuestas
    self.material_id = material_id

  def __getitem__(self):#,conocimiento_id, preguntas, respuestas):
    return [self.conocimiento_id,self.preguntas,self.respuestas]

class Entidad:
  def __init__(self, nombre, columnas, datos):
    self.nombre = nombre
    self.columnas = columnas
    self.datos = datos
    
  def get_col_idx(self, columna):
    return self.columnas.index(columna)

  def get_col_values(self, columna):
    col_idx = self.get_col_idx(columna)
    return [d[col_idx] for d in self.datos]
  
  def get_values_by_query(self, query): # query = [{'columna': 'p1', 'valor': 'v1'}, {'columna': 'p2', 'valor': 'v2'}]
    for fila in self.datos:
      matches = [True if q['valor'] in fila[self.get_col_idx(q['columna'])] else False for q in query] # Mejorar igualdad
      if np.all(matches): 
        values = {c:f for c, f in zip(self.columnas, fila)}
        return values
      
  def get_value(self, columna, fila_idx):
    col_idx = self.get_col_idx(columna)
    return self.datos[fila_idx][col_idx]


def tratamiento(text):
  text = text.lower()
  text = re.sub(r'[^@_a-zá-úñÑ0-9\s]+', ' ', text) # tomamos en cuenta @ y _
  text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
  text = text.split()
  return ' '.join(text)

def ngrams(text, n):
  ngrams = zip(*[text[i:] for i in range(n)])
  ngrams = [''.join(ng) for ng in ngrams]
  return ngrams

def semhash(text, n):
  tokens = []
  for t in text.split():
    if(t[0] != '@'):
      t = '#{}#'.format(t)
      tokens += ngrams(t, n)
  return ' '.join(tokens)

n = 3 #tamaño n-gram

def entrenarModelo(conocimientos,tema_id):
  vectorizer = CountVectorizer(token_pattern='[#a-zñ0-9]+')
  conocimiento_ids = [c.conocimiento_id for c in conocimientos]

  x_train = []
  y_train = []
  
  for c in conocimientos:
    x_train.extend([tratamiento(m) for m in c.preguntas])
    y_train.extend([conocimiento_ids.index(c.conocimiento_id)]*len(c.preguntas))

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
  
  filename = os.path.join('chatbot','models',tema_id+'.sav')
  pickle.dump(model, open(filename, 'wb'))
  FirebaseStorage.child('models',tema_id+'.sav').put(os.path.join('chatbot','models',tema_id+'.sav'))

  filenameVectorizer = os.path.join('chatbot','vectorizer',tema_id+'.sav')
  pickle.dump(vectorizer, open(filenameVectorizer, 'wb'))
  FirebaseStorage.child('vectorizer',tema_id+'.sav').put(os.path.join('chatbot','vectorizer',tema_id+'.sav'))
  
  return score

def cargarModelo(tema_id):
  FirebaseStorage.child('models',tema_id+'.sav').download(os.path.join('chatbot','models',tema_id+'.sav'))
  FirebaseStorage.child('vectorizer',tema_id+'.sav').download(os.path.join('chatbot','vectorizer',tema_id+'.sav'))
  filename = os.path.join('chatbot','models',tema_id+'.sav')
  model = pickle.load(open(filename, 'rb'))

  filenameVectorizer = os.path.join('chatbot','vectorizer',tema_id+'.sav')
  vectorizer = pickle.load(open(filenameVectorizer, 'rb'))

  modelos.update({tema_id:model})  
  vectorizers.update({tema_id:vectorizer})

def cargarVariosModelos(temas):
  for tema_id in temas:
    FirebaseStorage.child('models',tema_id+'.sav').download(os.path.join('chatbot','models',tema_id+'.sav'))
    FirebaseStorage.child('vectorizer',tema_id+'.sav').download(os.path.join('chatbot','vectorizer',tema_id+'.sav'))
    filename = os.path.join('chatbot','models',tema_id+'.sav')
    filenameVectorizer = os.path.join('chatbot','vectorizer',tema_id+'.sav')
    if(os.path.exists(filename)):
      model = pickle.load(open(filename, 'rb'))
      modelos.update({tema_id:model})  
      vectorizer = pickle.load(open(filenameVectorizer, 'rb'))
      vectorizers.update({tema_id:vectorizer})

# Respuesta
def obtener_distancia_promedio(arr1, arr2): # deben tener igual tamaño
  n = len(arr1)
  return np.sum([obtener_distancia(arr1[idx], arr2[idx]) for idx in range(n)]) / n

def obtener_distancia(texto1, texto2):
  texto1 = texto1.lower() # !!! por cambiar, puede ser tratamiento(texto1)
  texto2 = texto2.lower() # !!! por cambiar, puede ser tratamiento(texto2)
  return distancia_levenshtein(texto1, texto2)

def distancia_levenshtein(s, t, costs=(1, 1, 1)):
    rows = len(s)+1
    cols = len(t)+1
    deletes, inserts, substitutes = costs
    
    dist = [[0 for x in range(cols)] for x in range(rows)]
    
    for row in range(1, rows):
        dist[row][0] = row * deletes
    for col in range(1, cols):
        dist[0][col] = col * inserts
        
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0
            else:
                cost = substitutes
            dist[row][col] = min(dist[row-1][col] + deletes,
                                 dist[row][col-1] + inserts,
                                 dist[row-1][col-1] + cost)
 
    return dist[row][col]

def get_entidades_requeridas(texto): # retorna [{'nombre': ?, 'columna': ?}, ...]
  entidades_requeridas = []
  for token in texto.split():
    if(token[0] == '@'): # si token inicia con @
      sub_token = token.split('@') # obtenemos [0]@[1]@[2]
      entidades_requeridas += [{
        'nombre': sub_token[1], 
        'columna': sub_token[2]
      }]
  return entidades_requeridas

def get_entidades_respondidas(texto, entidades_requeridas, tabla_entidades):
  tokens = texto.split()
  success = True
  
  for ent_req in entidades_requeridas:
    for tbl_ent in tabla_entidades:
      if tbl_ent.nombre == ent_req['nombre']: break # obtenemos la tabla entidad
        
    tbl_ent_col_values = tbl_ent.get_col_values(ent_req['columna']) # obtenemos los valores de tabla entidad
    max_dis = 3 # !!! limite por cambiar
    best_min_dis = np.inf
    best_val_tecv = ''
    del_idx_ini = 0
    del_idx_fin = 0
    
    for tecvs in tbl_ent_col_values: # buscando valores de entidades requeridas
      if not isinstance(tecvs, list): tecvs = [tecvs] # convirtiendo si o si a lista
      for tecv in tecvs:
        tokens_tecv = tecv.split()
        n = len(tokens_tecv) # numero de tokens a comparar a la vez
        
        if n < 4: # limitar numero de tokens que pueden compararse
          for idx in range(len(tokens)-n+1):
            tokens_n = tokens[idx:idx+n]
            dis = obtener_distancia_promedio(tokens_tecv, tokens_n) # comparación de distancias entre array de tokens

            if dis < max_dis and dis < best_min_dis:
              best_val_tecv = ' '.join(tokens_tecv)
              best_min_dis = dis
              del_idx_ini = idx
              del_idx_fin = idx+n
    
    del tokens[del_idx_ini:del_idx_fin]
    ent_req['valor'] = best_val_tecv
    
    if best_val_tecv == '': success = False    
      
  return entidades_requeridas, success

def get_conocimiento_por_pregunta(pregunta, conocimientos, model, vectorizer):
  x_semhash = [semhash(pregunta, n)]
  x_vector = vectorizer.transform(x_semhash).toarray()
  probabilidades = model.predict_proba(x_vector)[0]
  idx = np.argmax(probabilidades)
  
  return conocimientos[idx]

def get_conocimiento_por_pregunta_2(pregunta, conocimientos, vectorizer):
  x = [p for c in conocimientos for p in c.preguntas]
  y = [c.conocimiento_id for c in conocimientos for _ in c.preguntas]

  sim = [similarity(pregunta, p, vectorizer) for p in x]
  idx = np.argmax(sim)

  for c in conocimientos:
    if c.conocimiento_id == y[idx]:
      return c
  
  return None

def similarity(text1, text2, vectorizer):
  v1 = vectorizer.transform([semhash(tratamiento(text1), n)]).toarray()[0]
  v2 = vectorizer.transform([semhash(tratamiento(text2), n)]).toarray()[0]
  aux = np.linalg.norm(v1)*np.linalg.norm(v2)
  return 0 if aux == 0 else np.dot(v1, v2)/aux

def get_queries(entidades_respondidas): # retorna [{?: [{'columna': ?, 'valor': ?}, ...]}, ...]
  queries = defaultdict(list)
  for er in entidades_respondidas:
    queries[er['nombre']].append({
        'columna': er['columna'],
        'valor': er['valor']
    })
    
  return queries

def get_values_by_queries(queries, tabla_entidades, perfil):
  values_by_queries = defaultdict(list)
  success = True
  values_by_queries['perfil'] = perfil
  
  for nombre, query in queries.items():
    for tbl_ent in tabla_entidades:
      if tbl_ent.nombre == nombre: break # obtenemos la tabla entidad
    
    values = tbl_ent.get_values_by_query(query)
    if values != None: # Si la query trajo resultados
      values_by_queries[nombre] = values
    else:
      success = False
      
  return values_by_queries, success
    
def construir_respuesta(respuesta_conocimiento, entidades_requeridas, values):
  for er in entidades_requeridas:
    try:
      value = values[er['nombre']][er['columna']]
      if isinstance(value, list): value = value[0]
      respuesta_conocimiento = respuesta_conocimiento.replace('@{}@{}'.format(er['nombre'],er['columna']), value)
    except:
      return '', False
    
  return respuesta_conocimiento, True

def responder(pregunta_usuario, conocimientos, tabla_entidades, tema_id, perfil):
  cargarModelo(tema_id)
  vectorizer = vectorizers.get(tema_id)
  model = modelos.get(tema_id)
  ############################################################
  respuesta = ''
  datos_ingresados = []
  datos_faltantes = []
  
  pregunta_usuario = tratamiento(pregunta_usuario)
  # conocimiento = get_conocimiento_por_pregunta(pregunta_usuario, conocimientos, model, vectorizer)
  conocimiento = get_conocimiento_por_pregunta_2(pregunta_usuario, conocimientos, vectorizer)
  material_id = conocimiento.material_id
  
  pregunta_conocimiento = conocimiento.preguntas[0]
  entidades_requeridas = get_entidades_requeridas(tratamiento(pregunta_conocimiento))
  entidades_respondidas, success = get_entidades_respondidas(pregunta_usuario, entidades_requeridas, tabla_entidades)
  if success: # todas las entidades requeridas fueron respondidas
    queries = get_queries(entidades_respondidas)
    values, success = get_values_by_queries(queries, tabla_entidades, perfil)
    if success: # se econtraron datos en la tabla que cumplen las entidades respondidas
      respuesta_conocimiento = random.choice(conocimiento.respuestas) # respuesta aleatoria
      entidades_requeridas = get_entidades_requeridas(tratamiento(respuesta_conocimiento))
      respuesta, success = construir_respuesta(respuesta_conocimiento, entidades_requeridas, values)
    
  datos_ingresados = [['@{}@{}'.format(er['nombre'], er['columna']), er['valor']] for er in entidades_respondidas if er['valor'] != '']
  datos_faltantes = ['@{}@{}'.format(er['nombre'], er['columna']) for er in entidades_respondidas if er['valor'] == '']
      
  return respuesta, material_id, datos_ingresados, datos_faltantes, success
  
 