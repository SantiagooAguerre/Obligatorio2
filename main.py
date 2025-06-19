import threading
import random
import time

DURACION_PARTIDO = 10
TIEMPO_MAX_CON_PELOTA = 5
TIEMPO_REACOMODO_ARQUERO = 3
PROB_GOL = 0.6
PROB_DELANTERO_RIVAL_QUITA = 0.3
PROB_DEFENSA_QUITA = 0.4
PROB_DEFENSA_INTERCEPTA = 0.3
PROB_PORTERO_INTERCEPTA_PASE = 0.2

pelota = threading.Semaphore(1)

partido_activo = True
equipo_actual = None
jugador_con_pelota = None
supero_delanteros = False
supero_defensa = False

# Contadores de goles
goles = {'A': 0, 'B': 0}

equipos = {
    'A': {
        'delanteros': ['A_D1', 'A_D2'],
        'defensa': 'A_DEF',
        'arquero': 'A_ARQ'
    },
    'B': {
        'delanteros': ['B_D1', 'B_D2'],
        'defensa': 'B_DEF',
        'arquero': 'B_ARQ'
    }
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def saque_inicial():
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = random.choice(['A', 'B'])
    jugador_con_pelota = random.choice(equipos[equipo_actual]['delanteros'])
    supero_delanteros = False
    supero_defensa = False
    log(f"¡Empieza el partido! Equipo {equipo_actual}, {jugador_con_pelota} con la pelota.")
    threading.Thread(target=control_jugador, args=(jugador_con_pelota,)).start()

def control_jugador(jugador):
    global jugador_con_pelota, supero_delanteros, supero_defensa

    while partido_activo:
        with pelota:
            if not partido_activo:  # Verificar nuevamente si el partido terminó
                return
            log(f"{jugador} tiene la pelota.")
            inicio = time.time()

            while time.time() - inicio < TIEMPO_MAX_CON_PELOTA and partido_activo:
                if jugador.endswith('D1') or jugador.endswith('D2'):
                    if not supero_delanteros:
                        return fase_frente_delanteros_rivales(jugador)
                    elif not supero_defensa:
                        return fase_frente_defensa(jugador)
                    else:
                        return fase_final_arco(jugador)
                elif jugador.endswith('DEF'):
                    return fase_defensa_contraataque(jugador)
                elif jugador.endswith('ARQ'):
                    return fase_arquero(jugador)
                time.sleep(0.5)

            if partido_activo:  # Solo si el partido sigue activo
                log(f"{jugador} tardó demasiado y pierde la pelota.")
                perder_pelota_defensa(jugador)
                return

def fase_frente_delanteros_rivales(jugador):
    global jugador_con_pelota, supero_delanteros
    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")
        if random.random() < PROB_DELANTERO_RIVAL_QUITA:
            log("¡El delantero rival intercepta el pase!")
            perder_pelota_delantero_rival()
            return True
        else:
            jugador_con_pelota = otro
            supero_delanteros = True
            log(f"{otro} recibe el pase y el equipo supera a los delanteros rivales.")
            threading.Thread(target=control_jugador, args=(otro,)).start()
            return True
    else:
        log(f"{jugador} intenta superar al delantero rival directamente.")
        if random.random() < PROB_DELANTERO_RIVAL_QUITA:
            log("¡El delantero rival le quita la pelota!")
            perder_pelota_delantero_rival()
            return True
        else:
            supero_delanteros = True
            log(f"{jugador} logra superar a los delanteros rivales.")
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def fase_frente_defensa(jugador):
    global jugador_con_pelota, supero_defensa
    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")
        if random.random() < PROB_DEFENSA_INTERCEPTA:
            log("¡El defensa intercepta el pase!")
            perder_pelota_defensa(jugador)
            return True
        else:
            jugador_con_pelota = otro
            supero_defensa = True
            log(f"{otro} recibe el pase y el equipo supera al defensa.")
            threading.Thread(target=control_jugador, args=(otro,)).start()
            return True
    else:
        log(f"{jugador} intenta superar al defensa directamente.")
        if random.random() < PROB_DEFENSA_QUITA:
            log("¡El defensa le quita la pelota!")
            perder_pelota_defensa(jugador)
            return True
        else:
            supero_defensa = True
            log(f"{jugador} logra superar al defensa.")
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def fase_final_arco(jugador):
    global goles
    accion = random.choice(['tiro', 'pase_tiro', 'duda'])
    if accion == 'tiro':
        log(f"{jugador} dispara al arco.")
        if random.random() < PROB_GOL:
            log("¡GOOOOOOL!")
            goles[equipo_actual] += 1
            reiniciar_partido()
        else:
            log("El arquero ataja el disparo.")
            portero = equipos[rival()]['arquero']
            threading.Thread(target=control_jugador, args=(portero,)).start()
        return True
    elif accion == 'duda':
        log(f"{jugador} duda y pierde la pelota.")
        perder_pelota_defensa(jugador)
        return True
    else:
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase final a {otro} para el tiro.")
        if random.random() < PROB_PORTERO_INTERCEPTA_PASE:
            log("¡El arquero intercepta el pase!")
            portero = equipos[rival()]['arquero']
            threading.Thread(target=control_jugador, args=(portero,)).start()
        else:
            jugador_con_pelota = otro
            log(f"{otro} recibe el centro y se prepara para disparar.")
            if random.random() < PROB_GOL:
                log("¡GOOOOOOL!")
                goles[equipo_actual] += 1
                reiniciar_partido()
            else:
                log("El arquero ataja el disparo.")
                portero = equipos[rival()]['arquero']
                threading.Thread(target=control_jugador, args=(portero,)).start()
            return True
        return True

def fase_defensa_contraataque(jugador):
    log(f"{jugador} recupera la pelota y pasa a un delantero.")
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def fase_arquero(jugador):
    global equipo_actual, supero_delanteros, supero_defensa
    log(f"{jugador} ataja y pasa a un delantero.")
    time.sleep(TIEMPO_REACOMODO_ARQUERO)
    # Asegurarse de que el arquero pasa a un delantero de SU equipo
    equipo_actual = jugador[0]  # La primera letra del jugador (A o B) es su equipo
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    log(f"{jugador} pasa a {nuevo}.")
    supero_delanteros = False
    supero_defensa = False
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def perder_pelota_delantero_rival():
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = rival()
    supero_delanteros = False
    supero_defensa = False
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    log(f"La pelota pasa al equipo {equipo_actual}. {nuevo} inicia el contraataque.")
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def perder_pelota_defensa(jugador):
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = rival()
    supero_delanteros = False
    supero_defensa = False
    defensa = equipos[equipo_actual]['defensa']
    jugador_con_pelota = defensa
    log(f"La pelota pasa al equipo {equipo_actual}. {defensa} inicia el contraataque.")
    threading.Thread(target=control_jugador, args=(defensa,)).start()

def fase_defensa_contraataque(jugador):
    global supero_delanteros, supero_defensa
    log(f"{jugador} recupera la pelota y pasa a un delantero.")
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    supero_delanteros = False
    supero_defensa = False
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def reiniciar_partido():
    global equipo_actual
    equipo_actual = rival()
    saque_inicial()

def rival():
    return 'A' if equipo_actual == 'B' else 'B'

def partido():
    global partido_activo
    saque_inicial()
    inicio = time.time()
    while time.time() - inicio < DURACION_PARTIDO:
        time.sleep(1)
    partido_activo = False
    log("¡Fin del partido!")
    log(f"Resultado final: Equipo A {goles['A']} - {goles['B']} Equipo B")

if __name__ == "__main__":
    partido()
