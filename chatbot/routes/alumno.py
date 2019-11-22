from flask import request, jsonify
from bson.json_util import dumps
from bson.objectid import ObjectId
from chatbot import app, mongo


@app.route('/obtenerAlumnosPorCurso', methods=['POST'])
def obtenerAlumnosPorCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula

  alumnos = coleccionMatricula.find({'curso_id':ObjectId(curso_id)})

  alumnos = [str(alumno['alumno_id']) for alumno in alumnos]

  alumnos = {
    'alumnos':alumnos
  }

  return jsonify(alumnos)

@app.route('/matricularAlumno', methods=['POST'])
def matricularAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula
  
  matriculaExiste = coleccionMatricula.find_one({
    '$and':[
      {'alumno_id': ObjectId(alumno_id)},
      {'curso_id': ObjectId(curso_id)}
    ]
  })

  if not matriculaExiste:
    matriculaNueva = coleccionMatricula.insert_one({
      'alumno_id': ObjectId(alumno_id),
      'curso_id': ObjectId(curso_id)
    }).inserted_id

    matricula = {
      'matricula_id' : str(matriculaNueva)
    }
  else:
    matricula = {
      'respuesta' : 'matricula ya existe'
    }

  return jsonify(matricula)

@app.route('/desmatricularAlumno', methods=['POST'])
def desmatricularAlumno():
  data = request.get_json() 

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  coleccionMatricula = mongo.db.matricula

  resultado = coleccionMatricula.delete_one({'alumno_id': ObjectId(alumno_id),'curso_id': ObjectId(curso_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)


@app.route('/obtenerAlumnos',methods=['GET'])
def obtenerAlumnos():
  coleccionAlumno = mongo.db.alumno

  alumno = coleccionAlumno.find()

  alumno = dumps(alumno)

  return jsonify(alumno)

@app.route('/obtenerAlumnoPorId',methods=['GET','POST'])
def obtenerAlumnoPorId():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionAlumno = mongo.db.alumno

  try:
    alumno = coleccionAlumno.find_one({'_id':ObjectId(alumno_id)})

    objetoAlumno = {
      'alumno_id': alumno_id,
      'nombre': alumno['nombre'],
      'apellido_paterno': alumno['apellido_paterno'],
      'apellido_materno': alumno['apellido_materno'],
      'codigo': alumno['codigo']
    }
  except:
    objetoAlumno = {}

  return  jsonify(objetoAlumno)

@app.route('/obtenerAlumnoPorNombre',methods=['POST'])
def obtenerAlumnoPorNombre():
  data = request.get_json()

  alumno_nombre = data['alumno_nombre']

  coleccionAlumno = mongo.db.alumno

  alumnos = coleccionAlumno.find({
    '$or':[
      {'nombre':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}},
      {'apellido_paterno':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}},
      {'apellido_materno':{'$regex':re.compile(alumno_nombre, re.IGNORECASE)}}
    ]
  })

  alumnos = dumps(alumnos)

  return jsonify(alumnos)

@app.route('/ingresarAlumno',methods=['POST'])
def ingresarAlumno():
  data = request.get_json()

  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']
  codigo = data['codigo']
  contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  alumnoIngresado = coleccionAlumno.insert_one({
    "nombre":nombre,
    "apellido_paterno":apellido_paterno,
    "apellido_materno":apellido_materno,
    "codigo":codigo,
    "contrasena":contrasena
  }).inserted_id

  alumno = {
    'alumno_id' : str(alumnoIngresado)
  }

  return jsonify(alumno)

@app.route('/actualizarContrasenaAlumno',methods=['POST'])
def actualizarContrasenaAlumno():
  data = request.get_json()
  
  alumno_id = data['alumno_id']
  contrasena_actual = data['contrasena_actual']
  contrasena_nueva = data['contrasena_nueva']

  coleccionAlumno = mongo.db.alumno

  alumno = coleccionAlumno.find_one({'_id' : ObjectId(alumno_id)})

  if contrasena_actual == alumno['contrasena']:
    resultado = coleccionAlumno.update_one(
      {'_id': ObjectId(alumno_id)},
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

@app.route('/actualizarAlumno',methods=['POST'])
def actualizarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']
  nombre = data['nombre']
  apellido_paterno = data['apellido_paterno']
  apellido_materno = data['apellido_materno']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.update_one(
    {'_id': ObjectId(alumno_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarAlumno',methods=['POST'])
def eliminarAlumno():
  data = request.get_json()

  alumno_id = data['alumno_id']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.delete_one({'_id': ObjectId(alumno_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)