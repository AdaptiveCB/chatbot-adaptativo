from flask import request, jsonify
from .. import app, mongo

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
  now = datetime.now()

  coleccionLogAlumno = mongo.db.logAlumno

  coleccionLogAlumno.insert_one({
    'alumno_id': alumno_id,
    'horaIngreso': now
  })