
import uuid
from datetime import timedelta

TARIFAS = {
    "normal": 150,     
    "aux_cocina": 200,
    "sup_cocina": 250,
    "sup_evento": 250
}

class Evento:
    def __init__(self, nombre, inicio):
        self.id = str(uuid.uuid4()) 
        self.nombre = nombre
        self.inicio = inicio
        self.fin = inicio + timedelta(hours=5) 
        
        self.requerimientos = {
            "normal": 7,       
            "aux_cocina": 1,
            "sup_cocina": 1,
            "sup_evento": 1
        }
        self.personal_asignado = [] 

    def cantidad_actual_rol(self, rol):
        return len([t for t in self.personal_asignado if t.rol == rol])

    def necesita_rol(self, rol):
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
        self.ids_eventos_disponibles = []
        self.eventos_asignados = [] 
    
    def agregar_disponibilidad(self, id_evento):
        self.ids_eventos_disponibles.append(id_evento)

    @property
    def prioridad_escasez(self):
        return len(self.ids_eventos_disponibles)

    def calcular_sueldo(self):
        tarifa = TARIFAS.get(self.rol, 150)
        return tarifa * len(self.eventos_asignados)

    def esta_disponible_logica(self, evento_obj):

        if evento_obj.id not in self.ids_eventos_disponibles:
            return False
        for evt_asignado in self.eventos_asignados:
            if (evento_obj.inicio < evt_asignado.fin) and (evento_obj.fin > evt_asignado.inicio):
                return False 
        

        return True
