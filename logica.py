def generar_horario(trabajadores, eventos):
    """
    Algoritmo principal que asigna personal.
    Reglas:
    1. VIPs (Supervisores/Cocina) entran SIEMPRE si están disponibles.
    2. Normales (Meseros) entran por prioridad de escasez y si hay cupo.
    """
    
    # Limpiamos asignaciones previas
    for e in eventos:
        e.personal_asignado = []
    for t in trabajadores:
        t.eventos_asignados = []

    # Roles VIP que ignoran el cupo máximo
    ROLES_VIP = ["aux_cocina", "sup_cocina", "sup_evento"]

    print("--- INICIANDO ASIGNACIÓN INTELIGENTE ---")

    # ORDENAMOS a los trabajadores: 
    # Primero los que pidieron POCOS eventos (Prioridad alta)
    trabajadores_ordenados = sorted(trabajadores, key=lambda x: x.prioridad_escasez)

    for evento in eventos:
        for trabajador in trabajadores_ordenados:
            
            # 1. Chequeo básico: ¿Quiere ir? ¿Choca horario?
            if trabajador.esta_disponible_logica(evento):
                
                # 2. Chequeo de Cupo Personal (¿Ya llenó su semana?)
                if len(trabajador.eventos_asignados) >= trabajador.cupo_deseado:
                    continue # Ya está lleno, pasamos al siguiente

                # 3. REGLAS DE ASIGNACIÓN
                es_vip = trabajador.rol in ROLES_VIP
                hay_cupo_rol = evento.necesita_rol(trabajador.rol)

                # SI es VIP -> Entra (No importa si 'necesita_rol' es falso)
                # SI NO es VIP -> Entra solo si 'necesita_rol' es verdadero
                if es_vip or hay_cupo_rol:
                    evento.personal_asignado.append(trabajador)
                    trabajador.eventos_asignados.append(evento)
                    # print(f"✅ {trabajador.nombre} asignado a {evento.nombre}")

    return trabajadores, eventos