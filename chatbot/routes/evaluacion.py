from flask import request, jsonify
from datetime import datetime, timedelta
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo

@app.route('/puntajeTotalAlumnoPorCurso', methods=['POST'])
def puntajeTotalAlumnoPorCurso():
  data = request.get_json()

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  fechas = []
  for i in range(5):
    fecha = (datetime.today() - timedelta(hours=5)) - timedelta(days=(4-i))
    fecha = datetime.strftime(fecha,'%d/%m/%Y')
    fecha = datetime.strptime(fecha,'%d/%m/%Y')
    fechas.append(fecha)

  coleccionTema = mongo.db.tema
  tema = coleccionTema.find_one({'curso_id':ObjectId(curso_id)})
  
  coleccionCuestionario = mongo.db.cuestionario
  cuestionarios = coleccionCuestionario.find({'tema_id':tema['_id']})

  listaCuestionarios = []
  for cuestionario in cuestionarios:
    listaCuestionarios.append(cuestionario['_id'])  

  coleccionEvaluacion = mongo.db.evaluacion

  puntajes = []

  for fecha in fechas:
    
    puntajeFecha = 0

    for cuestionario in listaCuestionarios:
      evaluacion = coleccionEvaluacion.find_one({'cuestionario_id':cuestionario,'alumno_id':ObjectId(alumno_id),'fecha':fecha})

      if(evaluacion):
        puntajeFecha = puntajeFecha + evaluacion['nota']
        
    objetoFecha = {}
    objetoFecha['fecha'] = datetime.strftime(fecha,'%d/%m/%Y')
    objetoFecha['puntajeTotal'] = puntajeFecha
    
    puntajes.append(objetoFecha)

  return jsonify(puntajes)

@app.route('/actualizarEvaluacion', methods=['GET','POST'])
def ingresarEvaluacion():
  data = request.get_json()

  alumno_id = data['alumno_id']
  cuestionario_id = data['cuestionario_id']
  fecha = data['fecha']
  nota = int(data['nota'])

  if fecha == '':
    objetoResultado = {
      'error': 'La fecha no puede ser vacía'
    }
    return jsonify(objetoResultado)
  
  try:
    fecha = datetime.strptime(fecha,'%d/%m/%Y') #str -> datetime
  except:
    objetoResultado = {
      'error': 'La fecha \'' + fecha + '\' no es válida. Enviar en el formato (dd/mm/aaaa)'
    }
    return jsonify(objetoResultado)

  coleccionEvaluacion = mongo.db.evaluacion

  existeEvaluacion = mongo.db.evaluacion.find_one({
    'alumno_id': ObjectId(alumno_id),
    'cuestionario_id': ObjectId(cuestionario_id),
    'fecha': fecha
  })

  if(existeEvaluacion):
    notaBD = existeEvaluacion['nota']

    if nota < notaBD:
      objetoResultado = {
        'error': 'La nota \'' + str(nota) + '\' no puede ser menor a la existente en la BD (' + str(notaBD) + ') en la misma fecha'
      }
    else:
      resultado = coleccionEvaluacion.update_one(
        {
          'alumno_id': ObjectId(alumno_id),
          'cuestionario_id': ObjectId(cuestionario_id),
          'fecha': fecha
        },
        {
          '$set':
              { 
                'nota': nota
              }
        }
      )

      objetoResultado = {
        'encontrado': resultado.matched_count,
        'modificado': resultado.modified_count
      }
  else:
    evaluacionIngresada = coleccionEvaluacion.insert_one({
      'alumno_id': ObjectId(alumno_id),
      'cuestionario_id': ObjectId(cuestionario_id),
      'fecha': fecha,
      'nota': nota
    }).inserted_id

    objetoResultado = {
      'evaluacion_id' : str(evaluacionIngresada)
    }

  return jsonify(objetoResultado)

@app.route('/obtenerEvaluacion', methods=['POST'])
def obtenerEvaluacion():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']
  alumno_id = data['alumno_id']

  coleccionEvaluacion = mongo.db.evaluacion

  evaluaciones = coleccionEvaluacion.find({
    'alumno_id':ObjectId(alumno_id),
    'cuestionario_id':ObjectId(cuestionario_id)
  })

  diccionarioEvaluaciones = {}
  
  for evaluacion in list(evaluaciones):
    diccionarioEvaluaciones[evaluacion['fecha']] = evaluacion['nota']
  
  resultados = []

  for key in sorted(diccionarioEvaluaciones.keys()):
    evaluacion = {}
    evaluacion['fecha'] = datetime.strftime(key,'%d/%m/%Y') #datetime -> str
    evaluacion['nota'] = diccionarioEvaluaciones[key]
    resultados.append(evaluacion)

  return jsonify(resultados)

@app.route('/eliminarEvaluacion', methods=['POST'])
def eliminarEvaluacion():
  data = request.get_json()

  alumno_id = data['alumno_id']
  cuestionario_id = data['cuestionario_id']
  fecha = data['fecha']

  try:
    fecha = datetime.strptime(fecha,'%d/%m/%Y') #str -> datetime
  except:
    objetoResultado = {
      'error': 'La fecha \'' + fecha + '\' no es válida. Enviar en el formato (dd/mm/aaaa)'
    }
    return jsonify(objetoResultado)

  coleccionEvaluacion = mongo.db.evaluacion

  resultado = coleccionEvaluacion.delete_one({
    'alumno_id': ObjectId(alumno_id),
    'cuestionario_id': ObjectId(cuestionario_id),
    'fecha': fecha
  })

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)