def generar_horario(trabajadores, eventos):
    
    for e in eventos:
        e.personal_asignado = []
    for t in trabajadores:
        t.eventos_asignados = []

    ROLES_VIP = ["aux_cocina", "sup_cocina", "sup_evento"]

    print("INICIANDO ASIGNACIÓN")
    trabajadores_ordenados = sorted(trabajadores, key=lambda x: x.prioridad_escasez)

    for evento in eventos:
        for trabajador in trabajadores_ordenados:
            
            if trabajador.esta_disponible_logica(evento):
                
                if len(trabajador.eventos_asignados) >= trabajador.cupo_deseado:
                    continue 

                es_vip = trabajador.rol in ROLES_VIP
                hay_cupo_rol = evento.necesita_rol(trabajador.rol)

                if es_vip or hay_cupo_rol:
                    evento.personal_asignado.append(trabajador)
                    trabajador.eventos_asignados.append(evento)

    return trabajadores, eventos
