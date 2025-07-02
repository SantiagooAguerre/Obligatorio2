import threading
import random
import time
import tkinter as tk
from tkinter import font as tkfont

DURACION_PARTIDO = 10
TIEMPO_MAX_CON_PELOTA = 5
TIEMPO_REACOMODO_ARQUERO = 3
PROB_GOL = 0.6
PROB_DELANTERO_RIVAL_QUITA = 0.3
PROB_DEFENSA_QUITA = 0.4
PROB_DEFENSA_INTERCEPTA = 0.3
PROB_PORTERO_INTERCEPTA_PASE = 0.2

# Configuración del juego
pelota = threading.Semaphore(1)
partido_activo = True
equipo_actual = None
jugador_con_pelota = None
supero_delanteros = False
supero_defensa = False
goles = {'A': 0, 'B': 0}

# Configuración de los equipos
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
        self.geometry("800x600")
        self.configure(bg='green')
        
        # Fuentes
        self.bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Helvetica", size=10)
        self.score_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        
        # Canvas para el campo
        self.canvas = tk.Canvas(self, width=800, height=500, bg='green')
        self.canvas.pack()
        
        # Dibujar el campo
        self.dibujar_campo()
        
        # Panel de información
        self.info_panel = tk.Frame(self, height=100, bg='white')
        self.info_panel.pack(fill='x')
        
        # Marcador
        self.score_label = tk.Label(self.info_panel, text="A 0 - 0 B", 
                                   font=self.score_font, bg='white')
        self.score_label.pack(side='top')
        
        # Log de eventos
        self.log_text = tk.Text(self.info_panel, height=4, width=80, 
                               font=self.normal_font, wrap='word')
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar = tk.Scrollbar(self.info_panel, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Temporizador
        self.time_label = tk.Label(self.info_panel, text="00:00", 
                                  font=self.bold_font, bg='white')
        self.time_label.pack(side='top', anchor='e', padx=10)
        
        # Inicializar jugadores
        self.jugadores_obj = {}
        self.pelota_obj = None
        self.inicializar_jugadores()
        
        # Temporizador del partido
        self.tiempo_inicio = time.time()
        self.actualizar_temporizador()
    
    def dibujar_campo(self):
        # Líneas del campo
        self.canvas.create_rectangle(50, 50, 750, 450, outline='white', width=2)
        self.canvas.create_line(400, 50, 400, 450, fill='white', width=2)
        
        # Áreas
        self.canvas.create_rectangle(50, 150, 150, 350, outline='white', width=2)  # Área izquierda
        self.canvas.create_rectangle(650, 150, 750, 350, outline='white', width=2)  # Área derecha
        
        # Puntos de penal
        self.canvas.create_oval(190, 245, 210, 255, fill='white')  # Penal izquierdo
        self.canvas.create_oval(590, 245, 610, 255, fill='white')  # Penal derecho
        
        # Arcos
        self.canvas.create_rectangle(40, 200, 50, 300, fill='white')  # Arco izquierdo
        self.canvas.create_rectangle(750, 200, 760, 300, fill='white')  # Arco derecho
    
    def inicializar_jugadores(self):
        # Posiciones iniciales
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
        
        # Crear jugadores en el canvas
        for jugador, pos in posiciones.items():
            equipo = jugador[0]
            color = equipos[equipo]['color']
            
            if 'ARQ' in jugador:
                # Arquero - círculo más grande
                obj = self.canvas.create_oval(pos[0]-15, pos[1]-15, pos[0]+15, pos[1]+15, 
                                            fill=color, outline='black')
            elif 'DEF' in jugador:
                # Defensa - rectángulo
                obj = self.canvas.create_rectangle(pos[0]-10, pos[1]-10, pos[0]+10, pos[1]+10, 
                                                  fill=color, outline='black')
            else:
                # Delanteros - círculos
                obj = self.canvas.create_oval(pos[0]-10, pos[1]-10, pos[0]+10, pos[1]+10, 
                                            fill=color, outline='black')
            
            # Etiqueta del jugador
            self.canvas.create_text(pos[0], pos[1]-20, text=jugador, fill='white', 
                                  font=self.normal_font)
            
            self.jugadores_obj[jugador] = obj
        
        # Crear pelota
        self.pelota_obj = self.canvas.create_oval(400-5, 250-5, 400+5, 250+5, fill='black')
    
    def mover_jugador(self, jugador, x, y):
        obj = self.jugadores_obj[jugador]
        if 'ARQ' in jugador:
            self.canvas.coords(obj, x-15, y-15, x+15, y+15)
        elif 'DEF' in jugador:
            self.canvas.coords(obj, x-10, y-10, x+10, y+10)
        else:
            self.canvas.coords(obj, x-10, y-10, x+10, y+10)
        
        # Mover también la etiqueta
        tags = self.canvas.gettags(obj)
        if tags and 'label' in tags[0]:
            label_tag = tags[0]
            self.canvas.coords(label_tag, x, y-20)
    
    def mover_pelota(self, x, y):
        self.canvas.coords(self.pelota_obj, x-5, y-5, x+5, y+5)
    
    def actualizar_marcador(self):
        self.score_label.config(text=f"A {goles['A']} - {goles['B']} B")
    
    def log(self, msg):
        timestamp = time.strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{timestamp}] {msg}\n")
        self.log_text.see('end')
        self.update()
    
    def actualizar_temporizador(self):
        if partido_activo:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            minutos = tiempo_transcurrido // 60
            segundos = tiempo_transcurrido % 60
            self.time_label.config(text=f"{minutos:02d}:{segundos:02d}")
            self.after(1000, self.actualizar_temporizador)
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
    
    # Actualizar posición visual
    actualizar_posicion_pelota(jugador_con_pelota)
    
    log(f"¡Empieza el partido! Equipo {equipo_actual}, {jugador_con_pelota} con la pelota.")
    threading.Thread(target=control_jugador, args=(jugador_con_pelota,)).start()

def actualizar_posicion_pelota(jugador):
    # Obtener posición del jugador
    obj = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    
    # Calcular posición central del jugador
    if 'ARQ' in jugador:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    elif 'DEF' in jugador:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    else:
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
    
    # Mover pelota a la posición del jugador
    field.mover_pelota(x, y)
    field.update()

def control_jugador(jugador):
    global jugador_con_pelota, supero_delanteros, supero_defensa

    while partido_activo:
        with pelota:
            if not partido_activo:  # Verificar nuevamente si el partido terminó
                return
            
            # Actualizar posición visual
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
                time.sleep(0.5)

            if partido_activo:  # Solo si el partido sigue activo
                log(f"{jugador} tardó demasiado y pierde la pelota.")
                perder_pelota_defensa(jugador)
                return

def fase_frente_delanteros_rivales(jugador):
    global jugador_con_pelota, supero_delanteros
    
    # 1. Identificar al delantero rival más cercano
    rival_pos = 'B' if equipo_actual == 'A' else 'A'
    delantero_rival = encontrar_oponente_mas_cercano(jugador, equipos[rival_pos]['delanteros'])
    
    # 2. Animación de superación (dribbling)
    animar_dribbling(jugador, delantero_rival)
    
    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")
        
        animar_pase(jugador, otro)
        
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
            
            # 3. Mover definitivamente al atacante adelante del defensor
            posicionar_adelante_de(jugador, delantero_rival)
            
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def posicionar_adelante_de(atacante, defensor):
    obj_def = field.jugadores_obj[defensor]
    coords_def = field.canvas.coords(obj_def)
    x_def = (coords_def[0] + coords_def[2]) / 2
    y_def = (coords_def[1] + coords_def[3]) / 2
    
    if equipo_actual == 'A':  # Avanzar hacia la derecha
        nuevo_x = x_def + 40
    else:  # Avanzar hacia la izquierda
        nuevo_x = x_def - 40
    
    field.mover_jugador(atacante, nuevo_x, y_def)
    actualizar_posicion_pelota(atacante)
    field.update()



def animar_dribbling(atacante, defensor):
    # Mover atacante hacia el defensor
    obj_atk = field.jugadores_obj[atacante]
    coords_atk = field.canvas.coords(obj_atk)
    x_atk = (coords_atk[0] + coords_atk[2]) / 2
    y_atk = (coords_atk[1] + coords_atk[3]) / 2
    
    obj_def = field.jugadores_obj[defensor]
    coords_def = field.canvas.coords(obj_def)
    x_def = (coords_def[0] + coords_def[2]) / 2
    y_def = (coords_def[1] + coords_def[3]) / 2
    
    # Animación de acercamiento
    pasos = 3
    for i in range(1, pasos + 1):
        nuevo_x = x_atk + (x_def - x_atk) * 0.3 * i/pasos
        field.mover_jugador(atacante, nuevo_x, y_atk)
        time.sleep(0.15)
    
    # Animación de superación (movimiento lateral + adelante)
    direccion = 1 if random.random() > 0.5 else -1  # Izquierda o derecha
    for i in range(1, 4):
        nuevo_x = x_def + 10 * direccion * i/3
        nuevo_y = y_def + 15 * i/3
        field.mover_jugador(atacante, nuevo_x, nuevo_y)
        actualizar_posicion_pelota(atacante)
        time.sleep(0.15)
    
    field.update()

def encontrar_oponente_mas_cercano(jugador, oponentes):
    obj_jug = field.jugadores_obj[jugador]
    coords_jug = field.canvas.coords(obj_jug)
    x_jug = (coords_jug[0] + coords_jug[2]) / 2
    y_jug = (coords_jug[1] + coords_jug[3]) / 2
    
    mas_cercano = None
    min_distancia = float('inf')
    
    for oponente in oponentes:
        obj_op = field.jugadores_obj[oponente]
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
    
    # Mover jugador atacante hacia adelante
    mover_hacia_adelante(jugador, 30)
    
    # Mover defensa rival hacia atrás (simulando que fue superado)
    rival_pos = 'B' if equipo_actual == 'A' else 'A'
    defensa_rival = equipos[rival_pos]['defensa']
    mover_hacia_atras(defensa_rival, 20)
    
    accion = random.choice(['pase', 'intentar_superar'])
    if accion == 'pase':
        otro = [d for d in equipos[equipo_actual]['delanteros'] if d != jugador][0]
        log(f"{jugador} intenta un pase a {otro}.")
        
        animar_pase(jugador, otro)
        
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
            
            # Mover más adelante al atacante exitoso
            mover_hacia_adelante(jugador, 40)
            
            threading.Thread(target=control_jugador, args=(jugador,)).start()
            return True

def fase_final_arco(jugador):
    global goles
    
    # Mover jugador hacia el arco
    mover_hacia_arco(jugador)
    
    accion = random.choice(['tiro', 'pase_tiro', 'duda'])
    if accion == 'tiro':
        log(f"{jugador} dispara al arco.")
        
        # Animación de tiro
        animar_tiro(jugador)
        
        if random.random() < PROB_GOL:
            log("¡GOOOOOOL!")
            goles[equipo_actual] += 1
            field.actualizar_marcador()
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
        
        # Animación de pase
        animar_pase(jugador, otro)
        
        if random.random() < PROB_PORTERO_INTERCEPTA_PASE:
            log("¡El arquero intercepta el pase!")
            portero = equipos[rival()]['arquero']
            threading.Thread(target=control_jugador, args=(portero,)).start()
        else:
            jugador_con_pelota = otro
            log(f"{otro} recibe el centro y se prepara para disparar.")
            
            # Animación de tiro
            animar_tiro(otro)
            
            if random.random() < PROB_GOL:
                log("¡GOOOOOOL!")
                goles[equipo_actual] += 1
                field.actualizar_marcador()
                reiniciar_partido()
            else:
                log("El arquero ataja el disparo.")
                portero = equipos[rival()]['arquero']
                threading.Thread(target=control_jugador, args=(portero,)).start()
            return True
        return True

def fase_defensa_contraataque(jugador):
    log(f"{jugador} recupera la pelota y pasa a un delantero.")
    
    # Mover defensa hacia atrás
    mover_hacia_atras(jugador, 30)
    
    nuevo = random.choice(equipos[equipo_actual]['delanteros'])
    jugador_con_pelota = nuevo
    
    # Animación de pase
    animar_pase(jugador, nuevo)
    
    threading.Thread(target=control_jugador, args=(nuevo,)).start()

def fase_arquero(jugador):
    global equipo_actual, supero_delanteros, supero_defensa
    log(f"{jugador} ataja y pasa a un delantero.")
    
    # Reposicionar jugadores antes de reiniciar
    reposicionar_jugadores()
    
    time.sleep(TIEMPO_REACOMODO_ARQUERO)
    
    equipo_actual = jugador[0]
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
    
    # Reposicionar jugadores antes del contraataque
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
    
    # Reposicionar jugadores antes del contraataque
    reposicionar_jugadores()
    
    defensa = equipos[equipo_actual]['defensa']
    jugador_con_pelota = defensa
    
    log(f"La pelota pasa al equipo {equipo_actual}. {defensa} inicia el contraataque.")
    threading.Thread(target=control_jugador, args=(defensa,)).start()

def reiniciar_partido():
    global equipo_actual
    equipo_actual = rival()
    
    # Reposicionar jugadores
    reposicionar_jugadores()
    
    saque_inicial()

def rival():
    return 'A' if equipo_actual == 'B' else 'B'

def mover_hacia_adelante(jugador, distancia):
    obj = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:  # Equipo A ataca hacia la derecha
        nuevo_x = min(x + distancia, 700)
    else:  # Equipo B ataca hacia la izquierda
        nuevo_x = max(x - distancia, 100)
    
    # Animación suave del movimiento
    pasos = 5
    for i in range(1, pasos + 1):
        temp_x = x + (nuevo_x - x) * i / pasos
        field.mover_jugador(jugador, temp_x, y)
        actualizar_posicion_pelota(jugador)
        time.sleep(0.1)
    
    field.update()

def mover_hacia_atras(jugador, distancia):
    obj = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:  # Equipo A retrocede hacia la izquierda
        nuevo_x = max(x - distancia, 100)
    else:  # Equipo B retrocede hacia la derecha
        nuevo_x = min(x + distancia, 700)
    
    # Animación suave del movimiento
    pasos = 5
    for i in range(1, pasos + 1):
        temp_x = x + (nuevo_x - x) * i / pasos
        field.mover_jugador(jugador, temp_x, y)
        time.sleep(0.1)
    
    field.update()

def mover_hacia_arco(jugador):
    obj = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    if 'A' in jugador:  # Equipo A ataca hacia la derecha
        nuevo_x = min(x + 80, 650)  # Hasta el área rival
    else:  # Equipo B ataca hacia la izquierda
        nuevo_x = max(x - 80, 150)  # Hasta el área rival
    
    field.mover_jugador(jugador, nuevo_x, y)
    actualizar_posicion_pelota(jugador)
    time.sleep(0.5)

def animar_pase(remitente, destinatario):
    # Obtener posiciones
    obj_rem = field.jugadores_obj[remitente]
    coords_rem = field.canvas.coords(obj_rem)
    x_rem = (coords_rem[0] + coords_rem[2]) / 2
    y_rem = (coords_rem[1] + coords_rem[3]) / 2
    
    obj_dest = field.jugadores_obj[destinatario]
    coords_dest = field.canvas.coords(obj_dest)
    x_dest = (coords_dest[0] + coords_dest[2]) / 2
    y_dest = (coords_dest[1] + coords_dest[3]) / 2
    
    # Animación de la pelota moviéndose
    pasos = 10
    for i in range(pasos + 1):
        x = x_rem + (x_dest - x_rem) * i / pasos
        y = y_rem + (y_dest - y_rem) * i / pasos
        field.mover_pelota(x, y)
        time.sleep(0.05)
    
    # Actualizar posición final
    actualizar_posicion_pelota(destinatario)

def animar_tiro(jugador):
    obj = field.jugadores_obj[jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    # Determinar dirección del tiro
    if 'A' in jugador:  # Tiro a la derecha
        x_objetivo = 750
    else:  # Tiro a la izquierda
        x_objetivo = 50
    
    # Posición vertical aleatoria dentro del arco
    y_objetivo = random.randint(200, 300)
    
    # Animación del tiro
    pasos = 15
    for i in range(pasos + 1):
        x_tiro = x + (x_objetivo - x) * i / pasos
        y_tiro = y + (y_objetivo - y) * i / pasos
        field.mover_pelota(x_tiro, y_tiro)
        time.sleep(0.05)
    
    # Si es gol, la pelota queda en el arco, sino vuelve al arquero
    if random.random() < PROB_GOL:
        field.mover_pelota(x_objetivo, y_objetivo)
    else:
        arquero = equipos[rival()]['arquero']
        actualizar_posicion_pelota(arquero)

def animar_cambio_posesion(nuevo_jugador):
    # Mover pelota al nuevo jugador
    obj = field.jugadores_obj[nuevo_jugador]
    coords = field.canvas.coords(obj)
    x = (coords[0] + coords[2]) / 2
    y = (coords[1] + coords[3]) / 2
    
    # Animación rápida
    field.mover_pelota(x, y)
    field.update()

def reposicionar_jugadores():
    # Posiciones iniciales
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
    
    # Pelota en el centro (aunque luego se moverá al jugador correspondiente)
    field.mover_pelota(400, 250)
    field.update()

def partido():
    global partido_activo
    saque_inicial()
    inicio = time.time()
    while time.time() - inicio < DURACION_PARTIDO and partido_activo:
        time.sleep(1)
    partido_activo = False
    log("¡Fin del partido!")
    log(f"Resultado final: Equipo A {goles['A']} - {goles['B']} Equipo B")

if __name__ == "__main__":
    field = FootballField()
    
    # Iniciar partido en un hilo separado
    threading.Thread(target=partido, daemon=True).start()
    
    field.mainloop()