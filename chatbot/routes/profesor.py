from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/obtenerProfesores',methods=['GET'])
def obtenerProfesores():
  coleccionProfesor = mongo.db.profesor

  profesor = coleccionProfesor.find()

  profesor = dumps(profesor)

  return jsonify(profesor)

@app.route('/obtenerProfesorPorId',methods=['GET','POST'])
def obtenerProfesorPorId():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionProfesor = mongo.db.profesor

  try:
    profesor = coleccionProfesor.find_one({'_id':ObjectId(profesor_id)})

    objetoProfesor = {
      'profesor_id': profesor_id,
      'nombre': profesor['nombre'],
      'apellido_paterno': profesor['apellido_paterno'],
      'apellido_materno': profesor['apellido_materno'],
      'codigo': profesor['codigo']
    }
  except:
    objetoProfesor = {}

  return  jsonify(objetoProfesor)

@app.route('/ingresarProfesor',methods=['POST'])
def ingresarProfesor():
  data = request.get_json()

  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  profesorIngresado = coleccionProfesor.insert_one({
    "nombre":nombre,
    "apellido_paterno":apellido_paterno,
    "apellido_materno":apellido_materno,
    "codigo":codigo,
    "contrasena":contrasena
  }).inserted_id

  profesor = {
    'profesor_id' : str(profesorIngresado)
  }

  return jsonify(profesor)

@app.route('/actualizarContrasenaProfesor',methods=['POST'])
def actualizarContrasenaProfesor():
  data = request.get_json()
  
  profesor_id = data['profesor_id']
  contrasena_actual = data['contrasena_actual']
  contrasena_nueva = data['contrasena_nueva']

  coleccionProfesor = mongo.db.profesor

  profesor = coleccionProfesor.find_one({'_id' : ObjectId(profesor_id)})

  if contrasena_actual == profesor['contrasena']:
    resultado = coleccionProfesor.update_one(
      {'_id': ObjectId(profesor_id)},
      {'$set':  
                {
                  'contrasena': contrasena_nueva
                }
      }
    )  

    objetoResultado = {
      'encontrado': resultado.matched_count,
      'modificado': resultado.modified_count
    }
  
  else:
    objetoResultado = {
      'respuestas': 'contrasena actual incorrecta'
    }

  return jsonify(objetoResultado)

@app.route('/actualizarProfesor',methods=['POST'])
def actualizarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  #codigo = data['codigo']
  #contrasena = data['contrasena']

  coleccionProfesor = mongo.db.profesor

  resultado = coleccionProfesor.update_one(
    {'_id': ObjectId(profesor_id)},
    {'$set':  
              {
                'nombre':nombre,
                'apellido_paterno':apellido_paterno,
                'apellido_materno':apellido_materno
                #'codigo': codigo,
                #'contrasena': contrasena
              }
    }
  )  

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarProfesor',methods=['POST'])
def eliminarProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionProfesor = mongo.db.profesor

  resultado = coleccionProfesor.delete_one({'_id': ObjectId(profesor_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)
