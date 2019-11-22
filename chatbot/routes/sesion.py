from flask import request, jsonify
from .. import app, mongo

@app.route('/iniciarSesionProfesor', methods=['GET','POST'])
def iniciarSesionProfesor():
  data = request.get_json()

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor
  profesor = coleccionProfesor.find_one({'codigo':codigo,'contrasena':contrasena})

  profesor_id = ""
  
  if(profesor):
    profesor_id = (str(profesor['_id']))
  
  objetoProfesor = {
    "profesor_id": profesor_id
  }

  return jsonify(objetoProfesor)