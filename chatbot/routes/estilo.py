from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo

@app.route('/obtenerEstiloAprendizajePorAlumnoId', methods=['POST'])
def obtenerEstiloAprendizajePorAlumnoId():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  estilos = {
    'alumno_id': alumno_id,
    'procesamiento': estiloAprendizaje['procesamiento']['categoria'],
    'procesamiento_valor': estiloAprendizaje['procesamiento']['valor'],
    'percepcion': estiloAprendizaje['percepcion']['categoria'],
    'percepcion_valor': estiloAprendizaje['percepcion']['valor'],
    'entrada': estiloAprendizaje['entrada']['categoria'],
    'entrada_valor': estiloAprendizaje['entrada']['valor'],
    'comprension': estiloAprendizaje['comprension']['categoria'],
    'comprension_valor': estiloAprendizaje['comprension']['valor']
  }

  return jsonify(estilos)


@app.route('/actualizarEstiloAprendizaje',methods=['POST'])
def actualizarEstiloAprendizaje():
  data = request.get_json()

  alumno_id = data['alumno_id']

  procesamiento_valor = data['procesamiento_valor']
  percepcion_valor = data['percepcion_valor']
  entrada_valor = data['entrada_valor']
  comprension_valor = data['comprension_valor']

  procesamiento_categoria = data['procesamiento']
  percepcion_categoria = data['percepcion']
  entrada_categoria = data['entrada']
  comprension_categoria = data['comprension']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  
  existeAlumno = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  if(existeAlumno):
    resultado = coleccionEstiloAprendizaje.update_one(
      {'alumno_id' : ObjectId(alumno_id)},
      {
        '$set':{
        'procesamiento':{'categoria': procesamiento_categoria,'valor': procesamiento_valor},
        'percepcion':{'categoria': percepcion_categoria,'valor': percepcion_valor},
        'entrada':{'categoria': entrada_categoria,'valor': entrada_valor},
        'comprension':{'categoria': comprension_categoria,'valor': comprension_valor}
        }
      }
    )

    respuesta = {
      'encontrado': resultado.matched_count,
      'modificado': resultado.modified_count
    }

  else:
    estiloAprendizajeIngresado = coleccionEstiloAprendizaje.insert_one(
      {
        'alumno_id' : ObjectId(alumno_id),
        'procesamiento':{'categoria': procesamiento_categoria,'valor': procesamiento_valor},
        'percepcion':{'categoria': percepcion_categoria,'valor': percepcion_valor},
        'entrada':{'categoria': entrada_categoria,'valor': entrada_valor},
        'comprension':{'categoria': comprension_categoria,'valor': comprension_valor}
      }
    ).inserted_id

    respuesta = {
      'estiloAprendizaje_id' : str(estiloAprendizajeIngresado)
    }

  return jsonify(respuesta)