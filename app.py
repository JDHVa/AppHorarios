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
    """
    Convierte un datetime a formato amigable en español.
    Ejemplo: 'Sábado 25 - 18:30'
    """
    dias = {
        0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves',
        4: 'Viernes', 5: 'Sábado', 6: 'Domingo'
    }
    
    # Obtenemos el nombre del día en español usando el número de la semana (0-6)
    nombre_dia = dias[fecha.weekday()]
    
    # Construimos la cadena final
    # Ejemplo: Sábado 25 - 14:00
    return f"{nombre_dia} {fecha.day} - {fecha.strftime('%H:%M')}"

# Registramos esta función para poder usarla en el HTML
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

    # El evento se crea con tus requerimientos por defecto (7 meseros, etc)
    nuevo_evento = Evento(nombre, dt_inicio)
    eventos_semana.append(nuevo_evento)
    
    return redirect(url_for('index'))

@app.route('/agregar_trabajador', methods=['POST'])
def agregar_trabajador():
    nombre = request.form['nombre']
    rol = request.form['rol'] # Viene del select (normal, sup_cocina, etc)
    
    # Este valor viene del input readonly calculado por JS
    try:
        cupo = int(request.form['cupo']) 
    except:
        cupo = 0

    nuevo_trabajador = Trabajador(nombre, rol, cupo)

    # Obtenemos los IDs de los eventos seleccionados
    ids_seleccionados = request.form.getlist('eventos_disponibles')

    # Guardamos los IDs en el trabajador
    for id_ev in ids_seleccionados:
        nuevo_trabajador.agregar_disponibilidad(id_ev)

    lista_trabajadores.append(nuevo_trabajador)
    return redirect(url_for('index'))

@app.route('/generar_horario')
def ruta_generar():
    # 1. Ejecutamos el algoritmo
    generar_horario(lista_trabajadores, eventos_semana)

    # 2. Mapa de Nombres (para el título o referencias)
    mapa_nombres = {e.id: e.nombre for e in eventos_semana}

    # --- NUEVO: Mapa de HORARIOS (Día y Hora cortos) ---
    # Esto convertirá el ID del evento en algo como "Sáb 18:30"
    dias_cortos = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}
    mapa_horarios = {}
    
    for e in eventos_semana:
        dia_str = dias_cortos[e.inicio.weekday()]
        hora_str = e.inicio.strftime('%H:%M')
        # Guardamos: "Sáb 18:30"
        mapa_horarios[e.id] = f"{dia_str} {hora_str}"

    # 3. Enviamos todo al HTML
    return render_template('resultados.html', 
                           eventos=eventos_semana, 
                           todos_trabajadores=lista_trabajadores,
                           mapa_eventos=mapa_nombres,
                           mapa_horarios=mapa_horarios) # <--- AGREGAMOS ESTO

# --- AGREGA ESTA NUEVA RUTA AL FINAL (ANTES DEL if __name__...) ---
@app.route('/agregar_trabajador_extra', methods=['POST'])
def agregar_trabajador_extra():
    """
    Agrega un trabajador desde la pantalla de resultados y 
    nos devuelve a la misma pantalla de resultados.
    """
    nombre = request.form['nombre']
    rol = request.form['rol']
    
    # El cupo viene del input readonly calculado por JS
    try:
        cupo = int(request.form['cupo']) 
    except:
        cupo = 0

    nuevo_trabajador = Trabajador(nombre, rol, cupo)

    # Obtenemos los IDs de los eventos seleccionados
    ids_seleccionados = request.form.getlist('eventos_disponibles')

    for id_ev in ids_seleccionados:
        nuevo_trabajador.agregar_disponibilidad(id_ev)

    lista_trabajadores.append(nuevo_trabajador)
    
    # REDIRECCIONAMOS A GENERAR_HORARIO (Para no irnos al inicio)
    return redirect(url_for('ruta_generar'))

@app.route('/reset')
def reset():
    global eventos_semana, lista_trabajadores
    eventos_semana = []
    lista_trabajadores = []
    return redirect(url_for('index'))

@app.route('/guardar_cambios', methods=['POST'])
def guardar_cambios():
    """
    Recibe un JSON con el nuevo orden:
    {
        "id_evento_1": ["id_trabajador_A", "id_trabajador_B"],
        "id_evento_2": ["id_trabajador_C"]
    }
    """
    nuevos_datos = request.get_json()
    
    # 1. Limpiamos las asignaciones actuales de todos los eventos
    #    (Para volver a llenarlas según lo que mandaste)
    for evento in eventos_semana:
        evento.personal_asignado = []
        
    # 2. Reasignamos según lo que nos llegó del "arrastrar y soltar"
    for evento_id, lista_ids_trabajadores in nuevos_datos.items():
        # Buscamos el objeto evento real
        evento_obj = next((e for e in eventos_semana if e.id == evento_id), None)
        
        if evento_obj:
            for trab_id in lista_ids_trabajadores:
                # Buscamos el objeto trabajador real en la lista global
                trab_obj = next((t for t in lista_trabajadores if t.id == trab_id), None)
                if trab_obj:
                    evento_obj.personal_asignado.append(trab_obj)
                    # Actualizamos también la lista interna del trabajador
                    # (Nota: en un sistema real habría que cuidar duplicados, 
                    # pero para este ajuste manual asumimos que lo mueves bien)
                    if evento_obj not in trab_obj.eventos_asignados:
                        trab_obj.eventos_asignados.append(evento_obj)

    return jsonify({"status": "success", "message": "Cambios guardados correctamente"})

if __name__ == '__main__':
    app.run(debug=True)