
import uuid
from datetime import timedelta

# Tarifas configurables
TARIFAS = {
    "normal": 150,      # Mesero normal
    "aux_cocina": 200,
    "sup_cocina": 250,
    "sup_evento": 250
}

class Evento:
    def __init__(self, nombre, inicio):
        self.id = str(uuid.uuid4()) 
        self.nombre = nombre
        self.inicio = inicio
        # Asumimos que el evento dura 5 horas por defecto para calcular choques
        self.fin = inicio + timedelta(hours=5) 
        
        # Estructura de cupos (Total 10 personas aprox)
        self.requerimientos = {
            "normal": 7,       # Meseros
            "aux_cocina": 1,
            "sup_cocina": 1,
            "sup_evento": 1
        }
        self.personal_asignado = [] 

    def cantidad_actual_rol(self, rol):
        """Cuenta cuántos hay de este rol asignados"""
        return len([t for t in self.personal_asignado if t.rol == rol])

    def necesita_rol(self, rol):
        """Verifica si falta gente en este rol (para NO VIPs)"""
        # Si el rol no está en la lista, asumimos cupo 0
        maximo = self.requerimientos.get(rol, 0)
        return self.cantidad_actual_rol(rol) < maximo

    def __repr__(self):
        return f"{self.nombre}"


class Trabajador:
    def __init__(self, nombre, rol, cupo_deseado):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.rol = rol  
        self.cupo_deseado = int(cupo_deseado)
        self.ids_eventos_disponibles = [] # IDs de los eventos que marcó
        self.eventos_asignados = [] 
    
    def agregar_disponibilidad(self, id_evento):
        self.ids_eventos_disponibles.append(id_evento)

    @property
    def prioridad_escasez(self):
        """
        Devuelve cuántos eventos pidió. 
        Menos eventos = Más prioridad.
        """
        return len(self.ids_eventos_disponibles)

    def calcular_sueldo(self):
        tarifa = TARIFAS.get(self.rol, 150) # 150 por defecto si no encuentra rol
        return tarifa * len(self.eventos_asignados)

    def esta_disponible_logica(self, evento_obj):
        """
        Validaciones básicas (Horario y Selección).
        NO checamos el cupo deseado aquí todavía para dar flexibilidad en el algoritmo.
        """
        # 1. ¿Marcó el evento?
        if evento_obj.id not in self.ids_eventos_disponibles:
            return False

        # 2. ¿Tiene choque de horario?
        for evt_asignado in self.eventos_asignados:
            if (evento_obj.inicio < evt_asignado.fin) and (evento_obj.fin > evt_asignado.inicio):
                return False 
        
        return True