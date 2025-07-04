import threading
import random
import time
import tkinter as tk
from tkinter import font as tkfont
from utilidades import (
    esperar_paso,
    step_event,
    DURACION_PARTIDO,
    TIEMPO_MAX_CON_PELOTA,
    TIEMPO_REACOMODO_ARQUERO,
    PROB_GOL,
    PROB_DELANTERO_RIVAL_QUITA,
    PROB_DEFENSA_QUITA,
    PROB_DEFENSA_INTERCEPTA,
    PROB_PORTERO_INTERCEPTA_PASE
)

pelota = threading.Semaphore(1)
partido_activo = True
equipo_actual = None
jugador_con_pelota = None
supero_delanteros = False
supero_defensa = False
goles = {'A': 0, 'B': 0}

equipos = {
    'A': {
        'delanteros': ['A_D1', 'A_D2'],
        'defensa': 'A_DEF',
        'arquero': 'A_ARQ',
        'color': 'blue'
    },
    'B': {
        'delanteros': ['B_D1', 'B_D2'],
        'defensa': 'B_DEF',
        'arquero': 'B_ARQ',
        'color': 'red'
    }
}

class FootballField(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Partido de Fútbol")
        self.geometry("1000x800")
        self.configure(bg='green')
        self.bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=10)
        self.score_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        self.canvas = tk.Canvas(self, width=800, height=500, bg='green')
        self.canvas.pack(pady=20)
        self.dibujar_campo()
        
        self.info_panel = tk.Frame(self, height=250, bg='white')
        self.info_panel.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        top_frame = tk.Frame(self.info_panel, bg='white')
        top_frame.pack(fill='x', pady=5)
        self.score_label = tk.Label(top_frame, text="A 0 - 0 B", 
                                   font=self.score_font, bg='white')
        self.score_label.pack(side='left', expand=True)
        
        self.time_label = tk.Label(top_frame, text="00:00", 
                                  font=self.bold_font, bg='white')
        self.time_label.pack(side='right', padx=20)
        
        log_frame = tk.Frame(self.info_panel, bg='white')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10,
                               font=self.normal_font, wrap='word')
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.jugadores_obj = {}
        self.pelota_obj = None
        self.inicializar_jugadores()
        self.tiempo_inicio = time.time()
        self.actualizar_temporizador()
    def dibujar_campo(self):
        self.canvas.create_rectangle(50, 50, 750, 450, outline='white', width=2)
        self.canvas.create_line(400, 50, 400, 450, fill='white', width=2)
        self.canvas.create_rectangle(50, 150, 150, 350, outline='white', width=2)
        self.canvas.create_rectangle(650, 150, 750, 350, outline='white', width=2)
        self.canvas.create_oval(190, 245, 210, 255, fill='white')
        self.canvas.create_oval(590, 245, 610, 255, fill='white')
        self.canvas.create_rectangle(40, 200, 50, 300, fill='white')
        self.canvas.create_rectangle(750, 200, 760, 300, fill='white')
    
    def inicializar_jugadores(self):
        posiciones = {
            'A_D1': (300, 200),
            'A_D2': (300, 300),
            'A_DEF': (250, 250),
            'A_ARQ': (100, 250),
            'B_D1': (500, 200),
            'B_D2': (500, 300),
            'B_DEF': (550, 250),
            'B_ARQ': (700, 250)
        }
        for jugador, pos in posiciones.items():
            equipo = jugador[0]
            color = equipos[equipo]['color']
            if 'ARQ' in jugador:
                obj = self.canvas.create_oval(pos[0]-15, pos[1]-15, pos[0]+15, pos[1]+15, fill=color, outline='black')
            elif 'DEF' in jugador:
                obj = self.canvas.create_rectangle(pos[0]-10, pos[1]-10, pos[0]+10, pos[1]+10, fill=color, outline='black')
            else:
                obj = self.canvas.create_oval(pos[0]-10, pos[1]-10, pos[0]+10, pos[1]+10, fill=color, outline='black')
            label = self.canvas.create_text(pos[0], pos[1]-20, text=jugador, fill='white', font=self.normal_font)
            self.jugadores_obj[jugador] = (obj, label)
        self.pelota_obj = self.canvas.create_oval(400-5, 250-5, 400+5, 250+5, fill='black')
    
    def mover_jugador(self, jugador, x, y):
        obj, label = self.jugadores_obj[jugador]
        if 'ARQ' in jugador:
            self.canvas.coords(obj, x-15, y-15, x+15, y+15)
        elif 'DEF' in jugador:
            self.canvas.coords(obj, x-10, y-10, x+10, y+10)
        else:
            self.canvas.coords(obj, x-10, y-10, x+10, y+10)
        self.canvas.coords(label, x, y-20)
        if jugador == jugador_con_pelota:
            self.mover_pelota(x, y)

        self.update()
    
    def mover_pelota(self, x, y):
        self.canvas.coords(self.pelota_obj, x-5, y-5, x+5, y+5)
    
    def actualizar_marcador(self):
        self.score_label.config(text=f"A {goles['A']} - {goles['B']} B")
    
    def log(self, msg):
        tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
        minutos = tiempo_transcurrido // 60
        segundos = tiempo_transcurrido % 60
        timestamp = f"{minutos:02d}:{segundos:02d}"
        self.log_text.insert('end', f"[{timestamp}] {msg}\n")
        self.log_text.see('end')
        self.update()
    
    def continuar_paso(self, event=None):
        step_event.set()

    def actualizar_temporizador(self):
        if partido_activo:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            minutos = tiempo_transcurrido // 60
            segundos = tiempo_transcurrido % 60
            self.time_label.config(text=f"{minutos:02d}:{segundos:02d}")
            self.after(1000, self.actualizar_temporizador)
            self.bind("<x>", self.continuar_paso)
        else:
            self.time_label.config(text="FIN")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    if hasattr(field, 'log'):
        field.log(msg)

def saque_inicial():
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = random.choice(['A', 'B'])
    jugador_con_pelota = random.choice(equipos[equipo_actual]['delanteros'])
    supero_delanteros = False
    supero_defensa = False
    reposicionar_jugadores()
    actualizar_posicion_pelota(jugador_con_pelota)
    field.update()
    
    log(f"¡Empieza el partido! Equipo {equipo_actual}, {jugador_con_pelota} con la pelota.")
    threading.Thread(target=control_jugador, args=(jugador_con_pelota,)).start()


def actualizar_posicion_pelota(jugador):
    obj, _ = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)

    if 'ARQ' in jugador:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    elif 'DEF' in jugador:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    else:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    field.mover_pelota(x, y)
    field.update()

def acompanar_con_companero(jugador):
    if not jugador.endswith('D1') and not jugador.endswith('D2'):
        return

    equipo = jugador[0]
    compañeros = [d for d in equipos[equipo]['delanteros'] if d != jugador]
    if not compañeros:
        return

    compañero = compañeros[0]
    obj, _ = field.jugadores_obj[compañero]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2

    avance = 130
    if equipo == 'A':
        nuevo_x = min(x + avance, 700)
    else:
        nuevo_x = max(x - avance, 100)

    pasos = 20
    for i in range(1, pasos + 1):
        temp_x = x + (nuevo_x - x) * i / pasos
        field.mover_jugador(compañero, temp_x, y)
        time.sleep(0.05)
    esperar_paso()


def control_jugador(jugador):
    global jugador_con_pelota, supero_delanteros, supero_defensa

    while partido_activo:
        with pelota:
            if not partido_activo:
                return
            actualizar_posicion_pelota(jugador)
            
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
                esperar_paso()

            if partido_activo:
                log(f"{jugador} demoró demasiado y le sacan la pelota.")
                perder_pelota_defensa(jugador)
                return

def fase_frente_delanteros_rivales(jugador):
    global jugador_con_pelota, supero_delanteros
    rival_pos = 'B' if equipo_actual == 'A' else 'A'
    delantero_rival = encontrar_oponente_mas_cercano(jugador, equipos[rival_pos]['delanteros'])
    animar_dribbling(jugador, delantero_rival)
    acompanar_con_companero(jugador)

    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")

        if random.random() < PROB_DELANTERO_RIVAL_QUITA:
            delantero_rival = encontrar_oponente_mas_cercano(jugador, equipos[rival_pos]['delanteros'])
            animar_pase(jugador, otro, interceptado_por=delantero_rival)
            log("El delantero rival intercepta el pase!")
            perder_pelota_delantero_rival()
            return True
        else:
            animar_pase(jugador, otro)
            jugador_con_pelota = otro
            supero_delanteros = True
            log(f"{otro} recibe el pase y el equipo supera a los delanteros rivales.")
            threading.Thread(target=control_jugador, args=(otro,)).start()
            return True

    else:
        log(f"{jugador} intenta superar al delantero rival directamente.")
        
        if random.random() < PROB_DELANTERO_RIVAL_QUITA:
            log("El delantero rival le saca la pelota!")
            animar_quita_pelota(delantero_rival, jugador)
            perder_pelota_delantero_rival()
            return True
        else:
            supero_delanteros = True
            log(f"{jugador} logra superar a los delanteros rivales.")
            posicionar_adelante_de(jugador, delantero_rival)
            
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def posicionar_adelante_de(atacante, defensor):
    obj_def, _ = field.jugadores_obj[defensor]
    coords_def = field.canvas.coords(obj_def)
    x_def = (coords_def[0] + coords_def[2]) / 2
    y_def = (coords_def[1] + coords_def[3]) / 2
    
    if equipo_actual == 'A':
        nuevo_x = x_def + 40
    else:
        nuevo_x = x_def - 40
    
    field.mover_jugador(atacante, nuevo_x, y_def)
    actualizar_posicion_pelota(atacante)
    field.update()

def animar_dribbling(atacante, defensor):
    obj_atk, _ = field.jugadores_obj[atacante]
    coords_atk = field.canvas.coords(obj_atk)
    x_atk = (coords_atk[0] + coords_atk[2]) / 2
    y_atk = (coords_atk[1] + coords_atk[3]) / 2

    obj_def, _ = field.jugadores_obj[defensor]
    coords_def = field.canvas.coords(obj_def)
    x_def = (coords_def[0] + coords_def[2]) / 2
    y_def = (coords_def[1] + coords_def[3]) / 2

    pasos = 9
    for i in range(1, pasos + 1):
        nuevo_x = x_atk + (x_def - x_atk) * 0.3 * i/pasos
        field.mover_jugador(atacante, nuevo_x, y_atk)
        time.sleep(0.05)
    esperar_paso()

    direccion = 1 if random.random() > 0.5 else -1
    for i in range(1, 4):
        nuevo_x = x_def + 10 * direccion * i/3
        nuevo_y = y_def + 15 * i/3
        field.mover_jugador(atacante, nuevo_x, nuevo_y)
        actualizar_posicion_pelota(atacante)
        time.sleep(0.15)
    esperar_paso()

    field.update()

def encontrar_oponente_mas_cercano(jugador, oponentes):
    obj_jug, _ = field.jugadores_obj[jugador]
    coords_jug = field.canvas.coords(obj_jug)
    x_jug = (coords_jug[0] + coords_jug[2]) / 2
    y_jug = (coords_jug[1] + coords_jug[3]) / 2
    
    mas_cercano = None
    min_distancia = float('inf')
    
    for oponente in oponentes:
        obj_op, _ = field.jugadores_obj[oponente]
        coords_op = field.canvas.coords(obj_op)
        x_op = (coords_op[0] + coords_op[2]) / 2
        y_op = (coords_op[1] + coords_op[3]) / 2
        
        distancia = ((x_jug - x_op)**2 + (y_jug - y_op)**2)**0.5
        if distancia < min_distancia:
            min_distancia = distancia
            mas_cercano = oponente
    
    return mas_cercano

def fase_frente_defensa(jugador):
    global jugador_con_pelota, supero_defensa
    mover_hacia_adelante(jugador, 30)
    rival_pos = 'B' if equipo_actual == 'A' else 'A'
    defensa_rival = equipos[rival_pos]['defensa']
    mover_hacia_atras(defensa_rival, 20)

    acompanar_con_companero(jugador)
    
    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")

        if random.random() < PROB_DEFENSA_INTERCEPTA:
            defensa_rival = equipos[rival_pos]['defensa']
            animar_pase(jugador, otro, interceptado_por=defensa_rival)
            log("El defensa intercepta el pase!")
            perder_pelota_defensa(jugador)
            return True
        else:
            animar_pase(jugador, otro)
            jugador_con_pelota = otro
            supero_defensa = True
            log(f"{otro} recibe el pase y el equipo supera al defensa.")
            threading.Thread(target=control_jugador, args=(otro,)).start()
            return True
    else:
        log(f"{jugador} intenta superar al defensa directamente.")
        
        if random.random() < PROB_DEFENSA_QUITA:
            log("El defensa le saca la pelota!")
            animar_quita_pelota(defensa_rival, jugador)
            perder_pelota_defensa(jugador)
            return True
        else:
            supero_defensa = True
            log(f"{jugador} logra superar al defensa.")
            mover_hacia_adelante(jugador, 40)
            
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def fase_final_arco(jugador):
    global goles
    mover_hacia_arco(jugador)
    acompanar_con_companero(jugador)
    
    accion = random.choice(['tiro', 'pase_tiro', 'duda'])
    if accion == 'tiro':
        log(f"{jugador} dispara al arco.")
        es_gol = animar_tiro(jugador)
        acompanar_con_companero(jugador)
        
        if es_gol:
            log("GOOOOOOL!")
            goles[equipo_actual] += 1
            field.actualizar_marcador()
            reiniciar_partido()
            return
        else:
            log("El arquero ataja el tiro.")
            portero = equipos[rival()]['arquero']
            threading.Thread(target=control_jugador, args=(portero,)).start()
        return True
    elif accion == 'duda':
        log(f"{jugador} duda y pierde la pelota.")
        
        rival_pos = 'B' if equipo_actual == 'A' else 'A'
        defensa_rival = equipos[rival_pos]['defensa']
        
        animar_quita_pelota(defensa_rival, jugador)
        perder_pelota_defensa(jugador)
        return True
    else:
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase final a {otro} para el tiro.")
        acompanar_con_companero(jugador)

        if random.random() < PROB_PORTERO_INTERCEPTA_PASE:
            portero = equipos[rival()]['arquero']
            log("El arquero intercepta el pase!")
            animar_pase(jugador, otro, interceptado_por=portero)
            threading.Thread(target=control_jugador, args=(portero,)).start()
        else:
            animar_pase(jugador, otro)
            jugador_con_pelota = otro
            log(f"{otro} recibe el centro y se prepara para disparar.")
            
            es_gol = animar_tiro(otro)
            if es_gol:
                log("GOOOOOOL!")
                goles[equipo_actual] += 1
                field.actualizar_marcador()
                reiniciar_partido()
                return
            else:
                log("El arquero ataja el disparo.")
                portero = equipos[rival()]['arquero']
                threading.Thread(target=control_jugador, args=(portero,)).start()
        return True

def fase_defensa_contraataque(jugador):
    global jugador_con_pelota
    
    log(f"{jugador} recupera la pelota y pasa a un delantero.")
    
    mover_hacia_atras(jugador, 30)
    
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    
    jugador_con_pelota = nuevo
    
    actualizar_posicion_pelota(nuevo)
    
    animar_pase(jugador, nuevo)
    
    threading.Thread(target=control_jugador, args=(nuevo,)).start()


def fase_arquero(jugador):
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa

    log(f"{jugador} ataja y pasa a un delantero.")
    reposicionar_jugadores()

    esperar_paso()
    
    equipo_actual = jugador[0]
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])

    jugador_con_pelota = nuevo
    actualizar_posicion_pelota(nuevo)
    field.update()
    
    log(f"{jugador} pasa a {nuevo}.")
    
    supero_delanteros = False
    supero_defensa = False
    
    threading.Thread(target=control_jugador, args=(nuevo,)).start()


def perder_pelota_delantero_rival():
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = rival()
    supero_delanteros = False
    supero_defensa = False
    reposicionar_jugadores()
    
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    
    log(f"La pelota pasa al equipo {equipo_actual}. {nuevo} inicia el contraataque.")
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def perder_pelota_defensa(jugador):
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    equipo_actual = rival()
    supero_delanteros = False
    supero_defensa = False
    reposicionar_jugadores()
    
    defensa = equipos[equipo_actual]['defensa']
    jugador_con_pelota = defensa
    
    log(f"La pelota pasa al equipo {equipo_actual}. {defensa} inicia el contraataque.")
    threading.Thread(target=control_jugador, args=(defensa,)).start()

def reiniciar_partido():
    global equipo_actual, jugador_con_pelota, supero_delanteros, supero_defensa
    
    equipo_que_recibio_el_gol = rival()
    equipo_actual = equipo_que_recibio_el_gol
    
    supero_delanteros = False
    supero_defensa = False
    
    reposicionar_jugadores()
    
    jugador_con_pelota = random.choice(equipos[equipo_que_recibio_el_gol]['delanteros'])
    
    actualizar_posicion_pelota(jugador_con_pelota)
    
    log(f"Saque inicial para el equipo {equipo_que_recibio_el_gol}! {jugador_con_pelota} con la pelota.")
    threading.Thread(target=control_jugador, args=(jugador_con_pelota,)).start()

def rival():
    return 'A' if equipo_actual == 'B' else 'B'

def mover_hacia_adelante(jugador, distancia):
    obj, _ = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:
        nuevo_x = min(x + distancia, 700)
    else:
        nuevo_x = max(x - distancia, 100)
    
    pasos = 15
    for i in range(1, pasos + 1):
        temp_x = x + (nuevo_x - x) * i / pasos
        field.mover_jugador(jugador, temp_x, y)
        actualizar_posicion_pelota(jugador)
        time.sleep(0.05)
    esperar_paso()
    
    field.update()

def mover_hacia_atras(jugador, distancia):
    obj, _ = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:
        nuevo_x = max(x - distancia, 100)
    else:
        nuevo_x = min(x + distancia, 700)
    
    pasos = 15
    for i in range(1, pasos + 1):
        temp_x = x + (nuevo_x - x) * i / pasos
        field.mover_jugador(jugador, temp_x, y)
        time.sleep(0.05)
    esperar_paso()
    
    field.update()

def mover_hacia_arco(jugador):
    obj, _ = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:
        nuevo_x = min(x + 80, 650)
    else:
        nuevo_x = max(x - 80, 150)
    
    field.mover_jugador(jugador, nuevo_x, y)
    actualizar_posicion_pelota(jugador)
    esperar_paso()

def animar_pase(remitente, destinatario, interceptado_por=None):
    obj_rem, _ = field.jugadores_obj[remitente]
    coords_rem = field.canvas.coords(obj_rem)
    x_rem = (coords_rem[0] + coords_rem[2]) / 2
    y_rem = (coords_rem[1] + coords_rem[3]) / 2

    obj_dest, _ = field.jugadores_obj[destinatario]
    coords_dest = field.canvas.coords(obj_dest)
    x_dest = (coords_dest[0] + coords_dest[2]) / 2
    y_dest = (coords_dest[1] + coords_dest[3]) / 2

    if interceptado_por:
        factor_intercep = 0.6
        x_intercep = x_rem + (x_dest - x_rem) * factor_intercep
        y_intercep = y_rem + (y_dest - y_rem) * factor_intercep

        obj_int, _ = field.jugadores_obj[interceptado_por]
        coords_int = field.canvas.coords(obj_int)
        x_int = (coords_int[0] + coords_int[2]) / 2
        y_int = (coords_int[1] + coords_int[3]) / 2

        pasos_int = 15
        for i in range(1, pasos_int + 1):
            xi = x_int + (x_intercep - x_int) * i / pasos_int
            yi = y_int + (y_intercep - y_int) * i / pasos_int
            field.mover_jugador(interceptado_por, xi, yi)
            time.sleep(0.03)

        pasos_pelota = 25
        for i in range(pasos_pelota + 1):
            x = x_rem + (x_intercep - x_rem) * i / pasos_pelota
            y = y_rem + (y_intercep - y_rem) * i / pasos_pelota
            field.mover_pelota(x, y)
            time.sleep(0.02)

        esperar_paso()
        actualizar_posicion_pelota(interceptado_por)

    else:
        pasos = 30
        for i in range(pasos + 1):
            x = x_rem + (x_dest - x_rem) * i / pasos
            y = y_rem + (y_dest - y_rem) * i / pasos
            field.mover_pelota(x, y)
            time.sleep(0.05)
        esperar_paso()
        actualizar_posicion_pelota(destinatario)

def animar_tiro(jugador):
    obj, _ = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2

    if 'A' in jugador:
        x_arco = 750
    else:
        x_arco = 50
    y_arco = random.randint(220, 280)

    sera_gol = random.random() < PROB_GOL

    if sera_gol:
        pasos = 20
        for i in range(pasos + 1):
            x_tiro = x + (x_arco - x) * i / pasos
            y_tiro = y + (y_arco - y) * i / pasos
            field.mover_pelota(x_tiro, y_tiro)
            time.sleep(0.02)
        esperar_paso()
        field.mover_pelota(x_arco, y_arco)
        return True

    else:
        portero = equipos[rival()]['arquero']
        obj_arq, _ = field.jugadores_obj[portero]
        coords_arq = field.canvas.coords(obj_arq)
        x_arq = (coords_arq[0] + coords_arq[2]) / 2
        y_arq = (coords_arq[1] + coords_arq[3]) / 2

        x_intercep = x + (x_arco - x) * 0.7
        y_intercep = y + (y_arco - y) * 0.7

        pasos_arq = 15
        for i in range(1, pasos_arq + 1):
            xa = x_arq + (x_intercep - x_arq) * i / pasos_arq
            ya = y_arq + (y_intercep - y_arq) * i / pasos_arq
            field.mover_jugador(portero, xa, ya)
            time.sleep(0.03)

        pasos_pelota = 30
        for i in range(pasos_pelota + 1):
            xp = x + (x_intercep - x) * i / pasos_pelota
            yp = y + (y_intercep - y) * i / pasos_pelota
            field.mover_pelota(xp, yp)
            time.sleep(0.02)

        esperar_paso()
        actualizar_posicion_pelota(portero)
        return False

def animar_cambio_posesion(nuevo_jugador):
    obj, _ = field.jugadores_obj[nuevo_jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    field.mover_pelota(x, y)
    field.update()

def animar_quita_pelota(defensor, poseedor):
    obj_def, _ = field.jugadores_obj[defensor]
    coords_def = field.canvas.coords(obj_def)
    x_def = (coords_def[0] + coords_def[2]) / 2
    y_def = (coords_def[1] + coords_def[3]) / 2

    obj_poseedor, _ = field.jugadores_obj[poseedor]
    coords_poseedor = field.canvas.coords(obj_poseedor)
    x_poseedor = (coords_poseedor[0] + coords_poseedor[2]) / 2
    y_poseedor = (coords_poseedor[1] + coords_poseedor[3]) / 2

    pasos = 10
    for i in range(1, pasos + 1):
        nuevo_x = x_def + (x_poseedor - x_def) * i / pasos
        nuevo_y = y_def + (y_poseedor - y_def) * i / pasos
        field.mover_jugador(defensor, nuevo_x, nuevo_y)
        time.sleep(0.05)
    esperar_paso()


def reposicionar_jugadores():
    posiciones = {
        'A_D1': (300, 200),
        'A_D2': (300, 300),
        'A_DEF': (250, 250),
        'A_ARQ': (100, 250),
        'B_D1': (500, 200),
        'B_D2': (500, 300),
        'B_DEF': (550, 250),
        'B_ARQ': (700, 250)
    }
    
    for jugador, pos in posiciones.items():
        field.mover_jugador(jugador, pos[0], pos[1])
    
    field.mover_pelota(400, 250)
    field.update()

def partido():
    global partido_activo
    saque_inicial()
    inicio = time.time()
    while time.time() - inicio < DURACION_PARTIDO and partido_activo:
        esperar_paso()
    partido_activo = False
    log("FIN DEL PARTIDO")
    log(f"Resultado final: Equipo A {goles['A']} - {goles['B']} Equipo B")

if __name__ == "__main__":
    field = FootballField()
    threading.Thread(target=partido, daemon=True).start()
    
    field.mainloop() # Hilo de la interfaz gráfica
    step_event.set()  # Permitir que el primer paso se ejecute inmediatamente