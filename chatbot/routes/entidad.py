from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/obtenerEntidadPorTema', methods=['GET','POST'])
def obtenerEntidadPorTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionEntidad = mongo.db.entidad
  
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})

  entidades = dumps(entidades)

  return jsonify(entidades)

@app.route('/ingresarEntidad',methods=['POST'])
def ingresarEntidad():
  data = request.get_json()

  nombre = data['nombre']
  columnas = data['columnas']
  datos = data['datos']
  tema_id = data['tema_id']

  coleccionEntidad = mongo.db.entidad

  entidadIngresada = coleccionEntidad.insert_one({
    'nombre':nombre,
    'columnas':columnas,
    'datos':datos,
    'tema_id':ObjectId(tema_id)
  }).inserted_id

  entidad = {
    'entidad_id' : str(entidadIngresada)
  }

  return jsonify(entidad)

@app.route('/actualizarEntidad',methods=['POST'])
def actualizarEntidad():
  data = request.get_json()

  entidad_id = data['entidad_id']
  nombre = data['nombre']
  columnas = data['columnas']
  datos = data['datos']
  # tema_id = data['tema_id']
  
  coleccionEntidad = mongo.db.entidad

  resultado = coleccionEntidad.update_one(
    {'_id': ObjectId(entidad_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'columnas':columnas,
                'datos':datos,
                # 'tema_id': ObjectId(tema_id)
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarEntidad',methods=['POST'])
def eliminarEntidad():
  data = request.get_json()

  entidad_id = data['entidad_id']

  coleccionEntidad = mongo.db.entidad

  resultado = coleccionEntidad.delete_one({'_id': ObjectId(entidad_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)