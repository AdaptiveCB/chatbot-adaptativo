from flask import request, jsonify, redirect
from datetime import datetime, timedelta
from bson.json_util import dumps
from bson.objectid import ObjectId
from ..semhash import cargarModelo,entrenarModelo,responder,Conocimiento,Entidad,cargarVariosModelos
from .. import app, mongo
# import random
# import re
# import os
# from tf_idf import limpiar, vocabulario, documento_a_vector, similitud_de_coseno

@app.route('/')
def home():
  return redirect("https://mitsuoysharag.github.io/TesisChatbotDocente_Vue")


# MATERIAL
@app.route('/obtenerMaterialPorTema', methods=['GET','POST'])
def obtenerListadoMaterial():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionMaterial = mongo.db.material
  
  materiales = coleccionMaterial.find({'tema_id':ObjectId(tema_id)})

  materiales = dumps(materiales)

  return jsonify(materiales)

@app.route('/obtenerMaterialPorId', methods=['GET','POST'])
def obtenerMaterialPorId():
  data = request.get_json()
  
  material_id = data['material_id']

  coleccionMaterial = mongo.db.material
  
  material = coleccionMaterial.find_one({'_id':ObjectId(material_id)})
  
  respuesta = {
    'material_id': str(material['_id']),
    'tema_id': str(material['tema_id']),
    'nombre': material['nombre'],
    'texto': material['texto'],
    'documento': material['documento'],
    'video': material['video'],
    'imagen': material['imagen'],
    'quiz': material['quiz'],
    'ejemplos': material['ejemplos'],
    'importancia': material['importancia'],
    'explicacion': material['explicacion'],
    'faq': material['faq']
  }
  
  return jsonify(respuesta)

@app.route('/obtenerMaterialPorAlumnoId', methods=['GET','POST'])
def obtenerMaterialPorAlumnoId():
  data = request.get_json()

  alumno_id = data['alumno_id']
  material_id = data['material_id']

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})

  coleccionMaterial = mongo.db.material
  material = coleccionMaterial.find_one({'_id':ObjectId(material_id)})
    
  if estiloAprendizaje['procesamiento']['valor']<=3 :
    activo=estiloAprendizaje['procesamiento']['valor']
    reflexivo=estiloAprendizaje['procesamiento']['valor']
  else:
    if estiloAprendizaje['procesamiento']['categoria']=='activo' :
      activo=estiloAprendizaje['procesamiento']['valor']
      reflexivo=0
    else:
      activo=0
      reflexivo=estiloAprendizaje['procesamiento']['valor']
    
  if estiloAprendizaje['percepcion']['valor']<=3 :
    sensorial=estiloAprendizaje['percepcion']['valor']
    intuitivo=estiloAprendizaje['percepcion']['valor']
  else:
    if estiloAprendizaje['percepcion']['categoria']=='intuitivo' :
      sensorial=0
      intuitivo=estiloAprendizaje['percepcion']['valor']
    else:
      sensorial=estiloAprendizaje['percepcion']['valor']
      intuitivo=0


  if estiloAprendizaje['entrada']['valor']<=3 :
    verbal=estiloAprendizaje['entrada']['valor']
    visual=estiloAprendizaje['entrada']['valor']
  else:
    if estiloAprendizaje['entrada']['categoria']=='visual' :
      verbal=0
      visual=estiloAprendizaje['entrada']['valor']
    else:
      verbal=estiloAprendizaje['entrada']['valor']
      visual=0


  if estiloAprendizaje['comprension']['valor']<=3 :
    secuencial=estiloAprendizaje['comprension']['valor']
    _global=estiloAprendizaje['comprension']['valor']
  else:
    if estiloAprendizaje['comprension']['categoria']=='secuencial' :
      secuencial=estiloAprendizaje['comprension']['valor']
      _global=0
    else:
      secuencial=0
      _global=estiloAprendizaje['comprension']['valor']

  recursosD = {}
  prioridad = []

  recursosD['tema_id']=str(material['tema_id'])
  recursosD['nombre']=material['nombre']  

  if(sensorial or secuencial or _global):
    recursosD['texto']=material['texto']
    dictTexto = {}
    dictTexto['item']='texto'
    dictTexto['puntaje']=max(sensorial,secuencial,_global)
    prioridad.append(dictTexto)

  if(intuitivo or verbal or reflexivo or secuencial):
    recursosD['importancia']=material['importancia']
    dictImportancia = {}
    dictImportancia['item']='importancia'
    dictImportancia['puntaje']=max(intuitivo,verbal,reflexivo,secuencial)
    prioridad.append(dictImportancia)

  if(intuitivo or _global):
    recursosD['explicacion']=material['explicacion']
    dictExplicacion = {}
    dictExplicacion['item']='explicacion'
    dictExplicacion['puntaje']=max(intuitivo,_global)
    prioridad.append(dictExplicacion)

  if(sensorial or activo or secuencial):
    recursosD['ejemplos']=material['ejemplos']
    dictEjemplos = {}
    dictEjemplos['item']='ejemplos'
    dictEjemplos['puntaje']=max(sensorial,activo,secuencial)
    prioridad.append(dictEjemplos)

  if(activo or secuencial):
    recursosD['quiz']=material['quiz']
    dictQuiz = {}
    dictQuiz['item']='quiz'
    dictQuiz['puntaje']=max(activo,secuencial)
    prioridad.append(dictQuiz)

  if(intuitivo or visual):
    recursosD['imagen']=material['imagen']
    dictImagen = {}
    dictImagen['item']='imagen'
    dictImagen['puntaje']=max(intuitivo,visual)
    prioridad.append(dictImagen)

  if(verbal):
    recursosD['documento']=material['documento']
    dictDocumento = {}
    dictDocumento['item']='documento'
    dictDocumento['puntaje']=verbal
    prioridad.append(dictDocumento)
      
  if(visual):
    recursosD['video']=material['video']
    dictVideo = {}
    dictVideo['item']='video'
    dictVideo['puntaje']=visual
    prioridad.append(dictVideo)

  if(sensorial or verbal or activo):
    recursosD['faq']=material['faq']
    dictFaq = {}
    dictFaq['item']='faq'
    dictFaq['puntaje']=max(sensorial,verbal,activo)
    prioridad.append(dictFaq)

  recursosD['prioridad']=prioridad

  return jsonify(recursosD)


@app.route('/ingresarMaterial', methods=['GET','POST'])
def ingresarMaterial():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  texto = data['texto']
  documento = data['documento']
  video = data['video']
  imagen = data['imagen']
  quiz = data['quiz'],
  ejemplos = data['ejemplos']
  importancia = data['importancia']

  try:
    explicacion = data['explicacion']
    faq = data['faq']
  except:
    explicacion = []
    faq = []

  coleccionMaterial = mongo.db.material

  materialIngresado = coleccionMaterial.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'texto': texto,
    'documento': documento,
    'video': video,
    'imagen': imagen,
    'quiz': quiz,
    'ejemplos': ejemplos,
    'importancia': importancia,
    'explicacion': explicacion,
    'faq': faq
  }).inserted_id

  material = {
    'material_id': str(materialIngresado)
  }

  return jsonify(material)

@app.route('/actualizarMaterial', methods=['GET','POST'])
def actualizarMaterial():
  data = request.get_json()

  material_id = data['material_id']

  tema_id = data['tema_id']
  nombre = data['nombre']
  texto = data['texto']
  documento = data['documento']
  video = data['video']
  imagen = data['imagen']
  quiz = data['quiz']
  ejemplos = data['ejemplos']
  importancia = data['importancia']
  
  try:
    explicacion = data['explicacion']
    faq = data['faq']
  except:
    explicacion = []
    faq = []

  coleccionMaterial = mongo.db.material

  resultado = coleccionMaterial.update_one(
    {'_id':ObjectId(material_id)},
    {'$set':
              {
                'tema_id': ObjectId(tema_id),
                'nombre': nombre,
                'texto': texto,
                'documento': documento,
                'video': video,
                'imagen': imagen,
                'quiz': quiz,
                'ejemplos': ejemplos,
                'importancia': importancia,
                'explicacion': explicacion,
                'faq': faq
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarMaterial', methods=['GET','POST'])
def eliminarMaterial():
  data = request.get_json()

  material_id = data['material_id']

  coleccionMaterial = mongo.db.material

  resultado = coleccionMaterial.delete_one({'_id': ObjectId(material_id)})
   
  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

# SESIÓN
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

    #logInicioSesionAlumno
    logInicioSesionAlumno(alumno['_id'])
  
  objetoAlumno = {
    "alumno_id": alumno_id
  }

  return jsonify(objetoAlumno)

def logInicioSesionAlumno(alumno_id):
  now = datetime.now()

  coleccionLogAlumno = mongo.db.logAlumno

  coleccionLogAlumno.insert_one({
    'alumno_id': alumno_id,
    'horaIngreso': now
  })

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



# TEMA
@app.route('/ingresarTema', methods=['GET','POST'])
def ingresarTema():
  data = request.get_json()

  curso_id = data['curso_id']
  nombre = data['nombre']

  coleccionTema = mongo.db.tema

  temaIngresado = coleccionTema.insert_one({
    'curso_id': ObjectId(curso_id),
    'nombre': nombre
  }).inserted_id

  nuevoTema_id = dumps(temaIngresado)

  return jsonify(nuevoTema_id)


@app.route('/obtenerTema', methods=['GET','POST'])
def obtenerTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionTema = mongo.db.tema

  tema = coleccionTema.find({"_id":ObjectId(tema_id)})

  tema = dumps(tema)

  return jsonify(tema)

@app.route('/obtenerTemaPorCurso', methods=['POST'])
def obtenerTemaPorCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionTema = mongo.db.tema

  temas = coleccionTema.find({"curso_id":ObjectId(curso_id)})

  temas = dumps(temas)

  return jsonify(temas)

# CUESTIONARIO

@app.route('/ingresarCuestionario', methods=['GET','POST'])
def ingresarCuestionario():
  data = request.get_json()

  tema_id = data['tema_id']
  nombre = data['nombre']
  preguntas = data['preguntas']
  nivel = data['nivel']
  tiempo = data['tiempo']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarioIngresado = coleccionCuestionario.insert_one({
    'tema_id': ObjectId(tema_id),
    'nombre': nombre,
    'preguntas': preguntas,
    'nivel': nivel,
    'tiempo': tiempo
  }).inserted_id

  cuestionario = {
    'cuestionario_id': str(cuestionarioIngresado)
  }

  return jsonify(cuestionario)

@app.route('/obtenerCuestionarioPorTema', methods=['POST'])
def obtenerCuestionarioPorTema():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionCuestionario = mongo.db.cuestionario

  cuestionarios = coleccionCuestionario.find({"tema_id":ObjectId(tema_id)})

  listaCuestionario = []

  for cuestionario in list(cuestionarios):
    objetoCuestionario = {}
    objetoCuestionario['cuestionario_id'] = str(cuestionario['_id'])
    objetoCuestionario['nombre'] = cuestionario['nombre']
    objetoCuestionario['preguntas'] = cuestionario['preguntas']
    objetoCuestionario['nivel'] = cuestionario['nivel']
    objetoCuestionario['tiempo'] = cuestionario['tiempo']
    listaCuestionario.append(objetoCuestionario)

  return jsonify(listaCuestionario)

@app.route('/actualizarCuestionario', methods=['GET','POST'])
def actualizarCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  nombre = data['nombre']
  preguntas = data['preguntas']
  nivel = data['nivel']
  tiempo = data['tiempo']

  coleccionCuestionario = mongo.db.cuestionario

  resultado = coleccionCuestionario.update_one(
    {'_id':ObjectId(cuestionario_id)},
    {'$set':
              {
                'nombre': nombre,
                'preguntas': preguntas,
                'nivel': nivel,
                'tiempo': tiempo
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarCuestionario',methods=['POST'])
def eliminarCuestionario():
  data = request.get_json()

  cuestionario_id = data['cuestionario_id']

  coleccionCuestionario = mongo.db.cuestionario

  resultado = coleccionCuestionario.delete_one({'_id': ObjectId(cuestionario_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

  
# EVALUACIÓN

@app.route('/puntajeTotalAlumnoPorCurso', methods=['POST'])
def puntajeTotalAlumnoPorCurso():
  data = request.get_json()

  alumno_id = data['alumno_id']
  curso_id = data['curso_id']

  fechas = []
  for i in range(5):
    fecha = datetime.today() - timedelta(days=(4-i))
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


# ESTILO APRENDIZAJE

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


# CRUD CONOCIMIENTO

@app.route('/ingresarConocimiento',methods=['GET','POST'])
def ingresarConocimiento():
  data = request.get_json()

  tema_id = data['tema_id']
  material_id = data['material_id']
  preguntas = data['preguntas']
  respuestas = data['respuestas']

  coleccionConocimiento = mongo.db.conocimiento

  nuevoConocimiento = coleccionConocimiento.insert_one({
    "tema_id" : ObjectId(tema_id),
    "material_id": ObjectId(material_id) if material_id != '' else '',
    "preguntas" : preguntas,
    "respuestas" : respuestas,
  }).inserted_id

  conocimiento = {
    'conocimiento_id': str(nuevoConocimiento)
  }

  return jsonify(conocimiento)

@app.route('/actualizarConocimiento',methods=['POST'])
def actualizarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']

  tema_id = data['tema_id']
  material_id = data['material_id']
  preguntas = data['preguntas']
  respuestas = data['respuestas']

  coleccionConocimiento = mongo.db.conocimiento

  resultado = coleccionConocimiento.update_one(
    {'_id': ObjectId(conocimiento_id)},
    {'$set':  
              {
                'tema_id': ObjectId(tema_id),
                'material_id': ObjectId(material_id) if material_id != '' else '',
                'preguntas': preguntas,
                'respuestas': respuestas,
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarConocimiento', methods=['POST'])
def eliminarConocimiento():
  data = request.get_json()

  conocimiento_id = data['conocimiento_id']

  coleccionConocimiento = mongo.db.conocimiento

  resultado = coleccionConocimiento.delete_one({'_id':ObjectId(conocimiento_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

@app.route('/obtenerConocimientoPorTema',methods=['GET','POST'])
def obtenerConocimiento():
  data = request.get_json()

  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  
  conocimiento = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})

  conocimiento = dumps(conocimiento)

  return jsonify(conocimiento)

# CRUD CURSO

@app.route('/obtenerCursoPorProfesor', methods=['POST'])
def obtenerCursoPorProfesor():
  data = request.get_json()

  profesor_id = data['profesor_id']

  coleccionCurso = mongo.db.curso

  cursos = coleccionCurso.find({'profesor_id':ObjectId(profesor_id)})

  cursos = dumps(cursos)

  return jsonify(cursos)

@app.route('/obtenerCursoPorAlumno', methods=['POST'])
def obtenerCursoPorAlumno():
  data = request.get_json()
  alumno_id = data['alumno_id']

  coleccionMatricula = mongo.db.matricula
  coleccionCurso = mongo.db.curso
  cursos = []

  matriculas = coleccionMatricula.find({'alumno_id':ObjectId(alumno_id)})
  
  for elemento in list(matriculas):
    cursos.append(coleccionCurso.find_one({'_id':ObjectId(elemento['curso_id'])}))

  return jsonify(dumps(cursos))

@app.route('/ingresarCurso',methods=['POST'])
def ingresarCurso():
  data = request.get_json()

  profesor_id = data['profesor_id']
  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  cursoIngresado = coleccionCurso.insert_one({
    'profesor_id': ObjectId(profesor_id),
    'nombre': nombre
  }).inserted_id

  curso = {
    'curso_id': str(cursoIngresado)
  }

  return jsonify(curso)

@app.route('/actualizarCurso',methods=['POST'])
def actualizarCurso():
  data = request.get_json()

  curso_id = data['curso_id']
  profesor_id = data['profesor_id']
  nombre = data['nombre']

  coleccionCurso = mongo.db.curso

  resultado = coleccionCurso.update_one(
    {'_id': ObjectId(curso_id)},
    {'$set':  
              {
                'profesor_id': ObjectId(profesor_id),
                'nombre': nombre
              }
    }
  )

  objetoResultado = {
    'encontrado': resultado.matched_count,
    'modificado': resultado.modified_count
  }

  return jsonify(objetoResultado)

@app.route('/eliminarCurso',methods=['POST'])
def eliminarCurso():
  data = request.get_json()

  curso_id = data['curso_id']

  coleccionCurso = mongo.db.curso

  resultado = coleccionCurso.delete_one({'_id': ObjectId(curso_id)})

  objetoResultado = {
    'eliminado': resultado.deleted_count
  }

  return jsonify(objetoResultado)

# CRUD ENTIDAD

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

# CRUD ALUMNO

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
  #codigo = data['codigo']
  #contrasena = data['contrasena']

  coleccionAlumno = mongo.db.alumno

  resultado = coleccionAlumno.update_one(
    {'_id': ObjectId(alumno_id)},
    {'$set':  
              { 
                'nombre': nombre,
                'apellido_paterno': apellido_paterno,
                'apellido_materno': apellido_materno
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

# CRUD PROFESOR

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

# RESPUESTA

@app.route('/obtenerRespuestaAlumno',methods=['GET','POST'])
def obtenerRespuesta():
  data = request.get_json()
  consulta = data['consulta']
  tema_id = data['tema_id']
  alumno_id = data['alumno_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimientos = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})
  coleccionEntidad = mongo.db.entidad
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})
  coleccionAlumno = mongo.db.alumno
  alumno = coleccionAlumno.find_one({'_id':ObjectId(alumno_id)})

  coleccionEstiloAprendizaje = mongo.db.estiloAprendizaje
  estiloAprendizaje = coleccionEstiloAprendizaje.find_one({'alumno_id' : ObjectId(alumno_id)})


  conocimientosBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 

  entidadBD = []
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))


  
  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, alumno)

  if(respuesta in ['texto','importancia','explicacion','ejemplos','quiz','imagen','documento','video']):
    respuesta = {
      'respuesta_item': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }
  else:
    respuesta = {
      'respuesta': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }

  return jsonify(respuesta)

@app.route('/obtenerRespuestaProfesor',methods=['GET','POST'])
def obtenerRespuestaProfesor():
  data = request.get_json()
  consulta = data['consulta']
  tema_id = data['tema_id']
  profesor_id = data['profesor_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimientos = coleccionConocimiento.find({'tema_id':ObjectId(tema_id)})
  coleccionEntidad = mongo.db.entidad
  entidades = coleccionEntidad.find({'tema_id':ObjectId(tema_id)})
  coleccionProfesor = mongo.db.profesor
  profesor = coleccionProfesor.find_one({'_id':ObjectId(profesor_id)})

  conocimientosBD = []
  for elemento in list(conocimientos):
    conocimientosBD.append(Conocimiento(str(elemento['_id']),elemento['preguntas'],elemento['respuestas'],elemento['material_id'])) 

  entidadBD = []
  for elemento in list(entidades):
    entidadBD.append(Entidad(elemento['nombre'],elemento['columnas'],elemento['datos']))   

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))

  respuesta, material_id, datos_ingresados, datos_faltantes, success = responder(consulta, conocimientosBD, entidadBD, tema_id, profesor)
  
  if(respuesta in ['texto','importancia','explicacion','ejemplos','quiz','imagen','documento','video']):
    respuesta = {
      'respuesta_item': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }
  else:
    respuesta = {
      'respuesta': respuesta,
      'material_id': str(material_id),
      'datos_ingresados': datos_ingresados,
      'datos_faltantes': datos_faltantes,
      'success': success
    }

  return jsonify(respuesta)

# ENTRENAMIENTO DEL MODELO

def procesamientoCategoriaMaterial(tema_id):
  conocimientosBDAux = []

  coleccionMaterial = mongo.db.material
  materiales = coleccionMaterial.find({'tema_id': ObjectId(tema_id)})

  recursos = []

  for material in list(materiales):
    obj_dict = {}
    obj_dict['nombre']=material['nombre']
    obj_dict['material']=str(material['_id'])
    obj_dict['faq']=material['faq']

    recursos.append(obj_dict)
  
  for recurso in recursos:
    arreglo_recurso = []

    dict_texto = {}
    preguntas = ['Que es '+recurso['nombre']]
    respuestas = ['texto']
    material = recurso['material']
    dict_texto['preguntas'] = preguntas
    dict_texto['respuestas'] = respuestas
    dict_texto['material_id'] = material
    arreglo_recurso.append(dict_texto)
  
    dict_importancia = {}
    preguntas = ['Por que es importante '+recurso['nombre']]
    respuestas = ['importancia']
    material = recurso['material']
    dict_importancia['preguntas'] = preguntas
    dict_importancia['respuestas'] = respuestas
    dict_importancia['material_id'] = material
    arreglo_recurso.append(dict_importancia)

    dict_explicacion = {}
    preguntas = ['Donde encuentro mas informacion de '+recurso['nombre']]
    respuestas = ['explicacion']
    material = recurso['material']
    dict_explicacion['preguntas'] = preguntas
    dict_explicacion['respuestas'] = respuestas
    dict_explicacion['material_id'] = material
    arreglo_recurso.append(dict_explicacion)
  
    dict_ejemplos = {}
    preguntas = ['Dime ejemplos de '+recurso['nombre']]
    respuestas = ['ejemplos']
    material = recurso['material']
    dict_ejemplos['preguntas'] = preguntas
    dict_ejemplos['respuestas'] = respuestas
    dict_ejemplos['material_id'] = material
    arreglo_recurso.append(dict_ejemplos)

    dict_quiz = {}
    preguntas = ['Hazme preguntas de '+recurso['nombre']]
    respuestas = ['quiz']
    material = recurso['material']
    dict_quiz['preguntas'] = preguntas
    dict_quiz['respuestas'] = respuestas
    dict_quiz['material_id'] = material
    arreglo_recurso.append(dict_quiz)

    dict_imagen = {}
    preguntas = ['Muestrame una imagen de '+recurso['nombre']]
    respuestas = ['imagen']
    material = recurso['material']
    dict_imagen['preguntas'] = preguntas
    dict_imagen['respuestas'] = respuestas
    dict_imagen['material_id'] = material    
    arreglo_recurso.append(dict_imagen)

    dict_documento = {}
    preguntas = ['Muestrame una documento de '+recurso['nombre']]
    respuestas = ['documento']
    material = recurso['material']
    dict_documento['preguntas'] = preguntas
    dict_documento['respuestas'] = respuestas
    dict_documento['material_id'] = material
    arreglo_recurso.append(dict_documento)

    dict_video = {}
    preguntas = ['Muestrame un video de '+recurso['nombre']]
    respuestas = ['video']
    material = recurso['material']
    dict_video['preguntas'] = preguntas
    dict_video['respuestas'] = respuestas
    dict_video['material_id'] = material
    arreglo_recurso.append(dict_video)

    for preguntaFrecuente in recurso['faq']:
      dict_faq = {}
      preguntas = [preguntaFrecuente['pregunta']]
      respuestas = [preguntaFrecuente['respuesta']]
      dict_faq['preguntas'] = preguntas
      dict_faq['respuestas'] = respuestas
      dict_faq['material_id'] = ''
      arreglo_recurso.append(dict_faq)

    for item in arreglo_recurso:
      aux = ObjectId()
      conocimientosBDAux.append(Conocimiento(aux,item['preguntas'],item['respuestas'],item['material_id']))
    
  return conocimientosBDAux

@app.route('/entrenar',methods=['GET','POST'])
def entrenar():
  # print('INICIO DE ENTRENAR')
  data = request.get_json()
  tema_id = data['tema_id']

  coleccionConocimiento = mongo.db.conocimiento
  conocimiento = coleccionConocimiento.find({
    'tema_id' : ObjectId(tema_id)  
  })

  conocimientosBD = []

  for elemento in list(conocimiento):
    conocimientosBD.append(Conocimiento(elemento['_id'],elemento['preguntas'],elemento['respuestas'],elemento['material_id']))

  conocimientosBD.extend(procesamientoCategoriaMaterial(tema_id))

  score = entrenarModelo(conocimientosBD,tema_id)
  # print('score:',score)

  # print('FIN DE ENTRENAR')

  return str(score)


# CARGAR MODELO
@app.route('/cargar',methods=['GET','POST'])
def cargar():
  data = request.get_json()

  tema_id = data['tema_id']
  
  cargarModelo(tema_id)

  return "Modelo cargado"

@app.route('/cargarVarios',methods=['GET','POST'])
def cargarVarios():
  coleccionTema = mongo.db.tema

  temas = coleccionTema.find()

  temas = list(temas)

  temas = [str(tema_id['_id']) for tema_id in temas]

  cargarVariosModelos(temas)

  return "ok"

cargarVarios()