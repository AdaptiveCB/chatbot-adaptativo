from flask import request, jsonify
from datetime import datetime, timedelta
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/pruebaTiempo', methods=['GET'])
def pruebaTiempo():
  coleccionLogTiempoAlumno = mongo.db.logTiempoAlumno

  tiempos = coleccionLogTiempoAlumno.find({})

  for t in list(tiempos):
    print(t['alumno_id'],t['tiempo'])
  
  return 'ja'

@app.route('/alumnos', methods=['GET'])
def alumnos():
  coleccionAlumno = mongo.db.alumno

  alumnos = coleccionAlumno.find({})

  for a in list(alumnos):
    print(a['_id'],a['apellido_paterno'],a['apellido_materno'])

  return 'j'


@app.route('/iniciarSesionAlumno', methods=['GET','POST'])
def iniciarSesionAlumno():
  data = request.get_json()

  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno
  alumno = coleccionAlumno.find_one({'codigo':codigo,'contrasena':contrasena})

  alumno_id = ""

  if(alumno):
    alumno_id = (str(alumno['_id']))

    logInicioSesionAlumno(alumno['_id'])
  
  objetoAlumno = {
    'alumno_id': alumno_id
  }

  return jsonify(objetoAlumno)

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
    'profesor_id': profesor_id
  }

  return jsonify(objetoProfesor)

@app.route('/tiempoTotalAlumnoPorDia', methods=['POST'])
def tiempoTotalAlumnoPorDia():
  data = request.get_json()

  alumno_id = data['alumno_id']

  fechas = []
  for i in range(5):
    fecha = (datetime.today() - timedelta(hours=5)) - timedelta(days=(4-i))
    fecha = datetime.strftime(fecha,'%d/%m/%Y')
    fecha = datetime.strptime(fecha,'%d/%m/%Y')
    fechas.append(fecha)
  
  coleccionLogTiempoAlumno = mongo.db.logTiempoAlumno

  tiempos = []

  for fecha in fechas:
    tiempoFecha = 0

    logTiempoAlumno = coleccionLogTiempoAlumno.find_one({'alumno_id':ObjectId(alumno_id),'fecha':fecha})

    if(logTiempoAlumno):
      tiempoFecha = tiempoFecha = logTiempoAlumno['tiempo']
    
    objetoFecha = {}
    objetoFecha['fecha'] = datetime.strftime(fecha,'%d/%m/%Y')
    objetoFecha['tiempoTotal'] = tiempoFecha

    tiempos.append(objetoFecha)

  return jsonify(tiempos)

@app.route('/obtenerTiempoAlumno', methods=['POST'])
def obtenerTiempoAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  fecha = data['fecha']

  fecha = datetime.strptime(fecha,'%d/%m/%Y')

  coleccionLogTiempoAlumno = mongo.db.logTiempoAlumno

  try:
    logTiempoAlumno = coleccionLogTiempoAlumno.find_one({
      'alumno_id':ObjectId(alumno_id),
      'fecha':fecha
    })

    tiempo = logTiempoAlumno['tiempo']
    
  except:
    tiempo = 0
  
  objetoResultado = {
    'tiempo': tiempo
  }

  return jsonify(objetoResultado)

@app.route('/actualizarTiempoAlumno', methods=['POST'])
def actualizarTiempoAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  fecha = data['fecha']
  tiempo = data['tiempo']


  if alumno_id == None:
    objetoResultado = {
      'error': 'El ID del alumno no puede ser nulo'
    }
  elif alumno_id == '':
    objetoResultado = {
      'error': 'El ID del alumno no puede ser vacio'
    }
  else:
    fecha = datetime.strptime(fecha,'%d/%m/%Y') #'%Y-%m-%d'

    coleccionLogTiempoAlumno = mongo.db.logTiempoAlumno

    existeLogTiempoAlumnoHoy = coleccionLogTiempoAlumno.find_one({
      'alumno_id':ObjectId(alumno_id),
      'fecha':fecha
    })

    if(existeLogTiempoAlumnoHoy):
      tiempoGuardado = existeLogTiempoAlumnoHoy['tiempo']

      if tiempo < tiempoGuardado:
        objetoResultado = {
          'error': 'El tiempo (' + str(tiempo) + ') no puede ser menor al existente en la BD (' + str(tiempoGuardado) + ')'
        }

      else:
        resultado = coleccionLogTiempoAlumno.update_one(
          {
            'alumno_id': ObjectId(alumno_id),
            'fecha': fecha
          },
          {
            '$set':
                    { 
                      'tiempo': tiempo
                    }
          }
        )

        objetoResultado = {
          'encontrado': resultado.matched_count,
          'modificado': resultado.modified_count
        }

    else:
      logIngresado = coleccionLogTiempoAlumno.insert_one({
        'alumno_id': ObjectId(alumno_id),
        'fecha': fecha,
        'tiempo': tiempo
      }).inserted_id

      objetoResultado = {
        'logIngresado_id' : str(logIngresado)
      }

  return jsonify(objetoResultado)

def logInicioSesionAlumno(alumno_id):
  now = datetime.today() - timedelta(hours=5)

  coleccionLogAlumno = mongo.db.logAlumno

  coleccionLogAlumno.insert_one({
    'alumno_id': alumno_id,
    'horaIngreso': now
  })