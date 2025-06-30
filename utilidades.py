import threading

step_event = threading.Event()

def esperar_paso():
    step_event.clear()
    step_event.wait()

DURACION_PARTIDO = 120
TIEMPO_MAX_CON_PELOTA = 5
TIEMPO_REACOMODO_ARQUERO = 3
PROB_GOL = 0.7
PROB_DELANTERO_RIVAL_QUITA = 0.1
PROB_DEFENSA_QUITA = 0.3
PROB_DEFENSA_INTERCEPTA = 0.2
PROB_PORTERO_INTERCEPTA_PASE = 0.2