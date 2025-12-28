from flask import Flask, render_template, request, redirect, url_for
from modelos import Trabajador, Evento, TARIFAS
from logica import generar_horario
from datetime import datetime
from flask import jsonify

app = Flask(__name__)

# Listas en memoria
eventos_semana = []
lista_trabajadores = []

def formato_fecha_es(fecha):

    dias = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    
    nombre_dia = dias[fecha.weekday()]
    

    return f"{nombre_dia} {fecha.day} - {fecha.strftime('%H:%M')}"

app.jinja_env.filters['fecha_es'] = formato_fecha_es

@app.route('/')
def index():
    return render_template('index.html', eventos=eventos_semana, trabajadores=lista_trabajadores)

@app.route('/agregar_evento', methods=['POST'])
def agregar_evento():
    nombre = request.form['nombre']
    fecha_str = request.form['fecha']
    hora_str = request.form['hora_inicio']
    
    try:
        dt_inicio = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return redirect(url_for('index'))

    nuevo_evento = Evento(nombre, dt_inicio)
    eventos_semana.append(nuevo_evento)
    
    return redirect(url_for('index'))

@app.route('/agregar_trabajador', methods=['POST'])
def agregar_trabajador():
    nombre = request.form['nombre']
    rol = request.form['rol']
    
    try:
        cupo = int(request.form['cupo']) 
    except:
        cupo = 0

    nuevo_trabajador = Trabajador(nombre, rol, cupo)

    ids_seleccionados = request.form.getlist('eventos_disponibles')

    for id_ev in ids_seleccionados:
        nuevo_trabajador.agregar_disponibilidad(id_ev)

    lista_trabajadores.append(nuevo_trabajador)
    return redirect(url_for('index'))

@app.route('/generar_horario')
def ruta_generar():
    generar_horario(lista_trabajadores, eventos_semana)

    mapa_nombres = {e.id: e.nombre for e in eventos_semana}

    dias_cortos = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}
    mapa_horarios = {}
    
    for e in eventos_semana:
        dia_str = dias_cortos[e.inicio.weekday()]
        hora_str = e.inicio.strftime('%H:%M')
        mapa_horarios[e.id] = f"{dia_str} {hora_str}"

    return render_template('resultados.html', 
                           eventos=eventos_semana, 
                           todos_trabajadores=lista_trabajadores,
                           mapa_eventos=mapa_nombres,
                           mapa_horarios=mapa_horarios)

@app.route('/agregar_trabajador_extra', methods=['POST'])
def agregar_trabajador_extra():

    nombre = request.form['nombre']
    rol = request.form['rol']
    
    try:
        cupo = int(request.form['cupo']) 
    except:
        cupo = 0

    nuevo_trabajador = Trabajador(nombre, rol, cupo)

    ids_seleccionados = request.form.getlist('eventos_disponibles')

    for id_ev in ids_seleccionados:
        nuevo_trabajador.agregar_disponibilidad(id_ev)

    lista_trabajadores.append(nuevo_trabajador)
    
    return redirect(url_for('ruta_generar'))

@app.route('/reset')
def reset():
    global eventos_semana, lista_trabajadores
    eventos_semana = []
    lista_trabajadores = []
    return redirect(url_for('index'))

@app.route('/guardar_cambios', methods=['POST'])
def guardar_cambios():

    nuevos_datos = request.get_json()
    
    for evento in eventos_semana:
        evento.personal_asignado = []
        
    for evento_id, lista_ids_trabajadores in nuevos_datos.items():
        evento_obj = next((e for e in eventos_semana if e.id == evento_id), None)
        
        if evento_obj:
            for trab_id in lista_ids_trabajadores:
                trab_obj = next((t for t in lista_trabajadores if t.id == trab_id), None)
                if trab_obj:
                    evento_obj.personal_asignado.append(trab_obj)

                    if evento_obj not in trab_obj.eventos_asignados:
                        trab_obj.eventos_asignados.append(evento_obj)

    return jsonify({"status": "success", "message": "Cambios guardados correctamente"})

if __name__ == '__main__':

    app.run(debug=True)
