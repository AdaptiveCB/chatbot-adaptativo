import numpy as np
import re

def limpiar(sentencia):
  documento = re.sub('(\?|¿)', '', sentencia.lower())
  return documento

def vocabulario(documentos):
  vocabulario = list(set([palabra for documento in documentos for palabra in documento.split()]))
  return vocabulario

def documento_a_vector(documento, vocabulario):
  vector = {palabra:0 for palabra in vocabulario}
  for palabra in documento.split():
    if palabra in vocabulario:
      vector[palabra] += 1
  return vector

def TF(documento, vocabulario):
  vector = documento_a_vector(documento, vocabulario)
  tf = {palabra: num_apariciones/len(documento.split()) for palabra, num_apariciones in vector.items()} # TF
  return tf

def IDF(documentos, vocabulario):
  idf = {}
  for palabra in vocabulario:
    num_apariciones = 0
    for documento in documentos:
      if palabra in documento.split():
        num_apariciones += 1
    idf[palabra] = np.log10(len(documentos)/num_apariciones) # IDF
  return idf

def TF_IDF(documento, documentos, vocabulario):
  tf = TF(documento, vocabulario)
  idf = IDF(documentos, vocabulario)
  tf_idf = {palabra: tf[palabra]*idf[palabra] for palabra in vocabulario} # TF*IDF
  return tf_idf

def similitud_de_coseno(documento_1, documento_2, documentos, vocabulario):
  tf_idf_1 = TF_IDF(documento_1, documentos, vocabulario)
  tf_idf_2 = TF_IDF(documento_2, documentos, vocabulario)
  
  vector_1 = np.array([*tf_idf_1.values()])
  vector_2 = np.array([*tf_idf_2.values()])
  cos = np.dot(vector_1, vector_2) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2)) # cos
  #cos = [round(valor,2) for valor in cos]
  return cos