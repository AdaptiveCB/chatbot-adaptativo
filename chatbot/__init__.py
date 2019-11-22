from flask import Flask
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['MONGO_DBNAME'] = 'chatbot'
app.config['MONGO_URI'] = 'mongodb+srv://chatbot:adaptive@cluster0-k4fnb.mongodb.net/chatbot?retryWrites=true&w=majority'

mongo = PyMongo(app)

from chatbot.routes import alumno,conocimiento,cuestionario,curso,entidad,estilo,evaluacion,home,material,modelo,profesor,respuesta,sesion,tema


# import random
# import re
# import os
# from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno