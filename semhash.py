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

conocimientos = [
  Conocimiento(
    intencion  = 'saludo', 
    preguntas   = ['Hola', 'Hey', 'Buenos días', 'Buenas tardes', 'Buenas noches','Buen día', 'Gusto de conversar contigo', 'Hola IA', 'Hi'],
    respuestas = ['Hola, ¿Cuál es tu duda?', 'Hola, ¿En qué puedo ayudarte?', 'Hola, ¿Cómo puedo servirte?']),
  Conocimiento(
    intencion  = 'estado',
    preguntas   = ['¿Estás bien?', '¿Cómo te encuentras?', '¿Cómo te sientes?', '¿Te encuentras bien?', '¿Qué tienes?', '¿Qué tal te sientes hoy?', '¿Cómo amaneciste hoy?'],
    respuestas = ['Estoy bien gracias', 'Me encuentro genial', 'La estoy pasando muy bien', 'Estoy teniendo un buen momento']),
  Conocimiento(
    intencion  = 'nombre',
    preguntas   = ['¿Cómo te llamas?', '¿Tienes nombre?', '¿Quién eres?', '¿Cuál es tu nombre?', '¿Cómo te haces llamar?', '¿Por qué nombre te conocen?'],
    respuestas = ['Mi nombre es IA', 'Me llamo IA', 'Me dicen IA', 'Me conocen como IA']),
  Conocimiento(
    intencion  = 'funcion',
    preguntas   = ['¿En qué puedes ayudarme?', 'Oye, ¿Para qué sirves?', '¿Por qué te crearon?', '¿Cuál es tu función o finalidad?', '¿Cómo me puedes ayudar?', 'Qué puedes hacer por mi?', '¿Para qué eres útil?', '¿Qué es lo que mejor sabes hacer?'],
    respuestas = ['Soy un bot creado para ayudarte con tus dudas.', 'Puedo ayudarte en lo que me preguntes.', 'Me encargo de despejar tus dudas.', 'Me crearon para ayudarte a estudiar']),
  Conocimiento(
    intencion  = 'edad',
    preguntas   = ['¿Cuántos años tienes?', 'Dime tu edad', '¿Cuándo naciste?', '¿En qué fecha te desarrollaron?', '¿Cuánto tiempo llevas funcionando?'],
    respuestas = ['Recién he sido creado', 'Soy muy joven, tengo menos de 1 año', 'Llevo']),
  Conocimiento(
    intencion  = 'agradecimiento',
    preguntas   = ['Gracias por tu ayuda', 'Muchas gracias', 'Gracias por la información', 'Gracias por todo', 'Mil gracias', 'Estoy muy agradecido', 'Me encuentro muy agradecido', 'Te lo agradezco', 'Qué amable', 'Eres muy amable'],
    respuestas = ['De nada', 'Feliz de ayudarte', 'Cuándo gustes', 'Cuándo quieras', 'Es un honor ayudarte']),
  Conocimiento(
    intencion  = 'despedida',
    preguntas   = ['Chau', 'Nos vemos', 'Adiós', 'Hasta pronto', 'Hasta Luego', 'Cuídate', 'Que te vaya bien', 'Estamos en contacto', 'Nos estamos viendo', 'Te veo luego', 'Saludos', 'Hasta mañana'],
    respuestas = ['Nos vemos, vuelve pronto', 'Hasta luego, espero haberte ayudado', 'Cuídate y no olvides estudiar', 'No dejes de estudiar']),
  Conocimiento(
    intencion = 'duda',
    preguntas = ['Tengo dudas sobre un tema','No me quedó claro un tema','No entendí la clase de hoy','Me perdí en la explicación del profesor'],
    respuestas = ['¿Qué tema dictaron?','¿En qué parte te perdiste?','¿Qué parte no entendiste bien?','¿Qué clase tuviste hoy?']),
  
  # Programación
  Conocimiento(
    intencion = 'programacion/función',
    preguntas = ['¿Qué es una función?'],
    respuestas = ['Una función es una parte de código que resuelva una tarea específica']),
  Conocimiento(
    intencion = 'programacion/clase',
    preguntas = ['¿Qué es una clase?'],
    respuestas = ['Una clase es un modelo que permite crear objetos con atributos y métodos similares']),
  Conocimiento(
    intencion = 'programacion/variable',
    preguntas = ['¿Qué es una variable?'],
    respuestas = ['La variable es un espacio de memoria que almacena un valor y es representado por un identificador']),
  Conocimiento(
    intencion = 'programacion/condicional',
    preguntas = ['¿Qué son estructuras condicionales?'],
    respuestas = ['Las estructuras condicionales permiten varian el flujo del programa']),
  Conocimiento(
    intencion = 'programacion/iterativa',
    preguntas = ['¿Qué son las estructuras iterativas?'],
    respuestas = ['Las esctructuras iterativas permiten ejecutar operaciones un número determinado de veces']),

  # Curso
  Conocimiento(
    intencion = 'horario',
    preguntas = ['¿A qué hora son las clases?', '¿En qué horario es el curso?'],
    respuestas = ['Los viernes de 12:00 a 16:00']),
  Conocimiento(
    intencion = 'examen',
    preguntas = ['¿A qué hora va a ser el examen?', '¿Cuándo va a ser el examen?'],
    respuestas = ['El examen será la siguiente clase a las 12:00']),
  Conocimiento(
    intencion = 'syllabus',
    preguntas = ['¿Cuales son los temas del curso?', '¿Qué temas aprenderemos en este curso?'],
    respuestas = ['Veremos los siguientes temas ...']),
  Conocimiento(
    intencion = 'tarea',
    preguntas = ['¿Que tarea han dejado para la próxima clase?', '¿Han dejado algún trabajo?'],
    respuestas = ['La tarea que se dejó es investigar sobre los chatbots.']),
  
  Conocimiento(
    intencion = 'progreso',
    preguntas = ['¿Cómo va mi progreso en el curso','¿Estoy mejorando en el curso?','¿Estoy teniendo un buen desempeño en el semestre?'],
    respuestas = ['Estas yendo bien, sigue así!','Vas muy bien, no pares de estudiar','Lo estas haciendo de maravilla, continúa esforzándote!']),
  Conocimiento(
    intencion = 'sugerencia',
    preguntas = ['¿Cómo puedo mejorar?','¿Qué debo hacer para obtener mejores resultados?','¿Cómo puedo sacar más nota?'],
    respuestas = ['Debes estudiar con más frecuencia','Repasa los temas que ya viste','Vuelve a leer tus apuntes']),
  Conocimiento(
    intencion = 'desarrollo de tesis',
    preguntas = ['¿Cómo debo avanzar la tesis?','¿Cómo eligo un tema de tesis?','¿Cuántos papers debería de leer?'],
    respuestas = ['Te recomiendo que eligas un tema relacionado a la rama que te guste.','Puedes comenzar leyendo 10 papers.','Puedes avanzar la tesis capítulo por capítulo.']),
  Conocimiento(
    intencion = 'estilo de aprendizaje',
    preguntas = ['¿Cuántos estilos de aprendizaje hay?','¿En qué modelo de aprendizaje te basas?'],
    respuestas = ['Me programaron bajo el modelo de aprendizaje de Felder-Silverman.','Según el modelo de Felder-Silverman hay 8 estilos de aprendizaje agrupados en 4 dimensiones']),
  Conocimiento(
    intencion = 'mi estilo de aprendizaje',
    preguntas = ['¿Cuál es mi estilo de aprendizaje?', 'Dime cual es mi perfil de aprendizaje'],
    respuestas = ['Tu estilo de aprendizaje es visual y global.']),
]

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
model = LogisticRegression(C=1.0, class_weight=None, dual=False,
          fit_intercept=True, intercept_scaling=1, max_iter=100,
          multi_class='ovr', n_jobs=1, penalty='l2', random_state=None,
          solver='liblinear', tol=0.0001, verbose=0, warm_start=False)
intenciones = []

def reemplazarConocimiento(conocimientoBD):
  global conocimientos
  conocimientos = conocimientoBD

def entrenarModelo():
  global intenciones
  intenciones = [c.intencion for c in conocimientos]
  x_train = []
  y_train = []
  
  for c in conocimientos:
    x_train.extend([m for m in c.preguntas])
    y_train.extend([intenciones.index(c.intencion)]*len(c.preguntas))
  
  # n = 3 #tamaño n-gram

  x_train_semhash = [semhash(x, n) for x in x_train]

  ngram_range=(3,3)
  # vectorizer = CountVectorizer(token_pattern='[#a-zñ0-9]+')
  vectorizer.fit(x_train_semhash)
  

  x_train_vector = vectorizer.transform(x_train_semhash).toarray()

  # model = LogisticRegression(C=1.0, class_weight=None, dual=False,
  #           fit_intercept=True, intercept_scaling=1, max_iter=100,
  #           multi_class='ovr', n_jobs=1, penalty='l2', random_state=None,
  #           solver='liblinear', tol=0.0001, verbose=0, warm_start=False)
  model.fit(x_train_vector, y_train)
  
  predicciones = model.predict(x_train_vector)
  score = metrics.accuracy_score(y_train, predicciones)
  
  print('Entrenamiento Finalizado')


def responder(pregunta):
  x_semhash = [semhash(pregunta, n)]
  x_vector = vectorizer.transform(x_semhash).toarray()
  prediccion = model.predict(x_vector)[0]
  intencion = intenciones[prediccion]

  # print('-' * 50)
  # print("Pregunta:", pregunta)
  # print("Semhash:", x_semhash) # print("Vector:", x_vector[0][:30], '...')
  # print("Intencion:", intencion)
  # pregunta = ""
  respuesta = ""
  pdf = ""
  video = ""
  conocimiento_id = ""
  for c in conocimientos:

    if c.intencion == intencion:
      # print("Respuesta:", random.choice(c.respuestas))
      conocimiento_id = c.intencion
      # pregunta = random.choice(c.preguntas)
      respuesta = random.choice(c.respuestas)
      pdf = c.pdf
      video = c.video
      break
  objeto = {
    'conocimiento_id':conocimiento_id,
    # 'pregunta':pregunta,
    'respuesta':respuesta,
    'pdf':pdf,
    'video':video
  }
  return objeto
  

# responder('me podrías decir cuál es tu nombre?, si es que tienes uno')
# responder('en qué podrias ayudarme tú?')
# responder('oye gracias por ayudarme, te pasaste')
# responder('dime cuál es tu edad anciano')
# responder('cómo mejoro?')
# responder('qué tema de tesis elijo?')
# responder('¿Qué entiendo por una variable?')
# responder('brother, estoy mejorando?')
# responder('que sería una variable?')
# responder('amigo, que es una función??')
# responder('cual es mi perfil o estilo de aprendizaje?')
# entrenarModelo()