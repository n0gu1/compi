# rover.py

import math
import time
import requests
from django.conf import settings

# URL del Rover (NodeMCU)
ROVER_URL = f"http://{getattr(settings, 'ROVER_IP', '192.168.4.1')}/"

# Retardos por letra (en segundos)
COMMAND_DELAYS = {
    "F": 0.1,   # calibrar para 1 vuelta de rueda
    "B": 0.2,
    "R": 0.5,   # 0.5s ≈ 90° de pivote
    "L": 0.5,
    "I": 0.5,
    "J": 0.5,
    "G": 0.5,
    "H": 0.5,
    "S": 0.1,
}

# Calibración: segundos que tarda en mover 1 cm real
CM_DELAY_PER_CM = 0.05

# Para rotar: 4 pulsos de R/L a 0.5s cada uno dan ~360°
PULSES_PER_REV = 4

def _send(letter: str) -> None:
    """
    Envía 'letter' al Rover y espera el delay configurado en COMMAND_DELAYS.
    """
    delay = COMMAND_DELAYS.get(letter, 0.5)
    try:
        requests.get(ROVER_URL, params={"State": letter}, timeout=2)
    except requests.RequestException as exc:
        print("⚠️  Rover sin respuesta:", exc)
    time.sleep(delay)

def translate(cmd: str, n: int) -> list[str]:
    if cmd == "avanzar_vlts":
        seq: list[str] = []
        letter = "F" if n > 0 else "B"
        for _ in range(abs(n)):
            seq.append(letter)
            seq.append("S")
        return seq

    if cmd in ("avanzar_ctms", "avanzar_mts"):
        letter = "F" if n > 0 else "B"
        return [letter] * abs(n)

    if cmd == "girar":
        if n == 1:  return ["R", "S"]
        if n == -1: return ["L", "S"]
        return ["F", "S"]

    if cmd == "rotar":
        # se usa execute(), no translate
        letter = "R" if n > 0 else "L"
        return [letter] * abs(n)

    if cmd in ("caminar", "moonwalk"):
        letter = "G" if n > 0 else "H"
        return [letter] * abs(n)

    return []

def execute(commands: list[list]) -> None:
    """
    Recorre la lista [['cmd', n], …] y envía cada comando al Rover.
    Se maneja 'circulo', 'cuadrado', 'rotar', 'caminar' y 'moonwalk'.
    """
    for cmd, n in commands:
        # --- Dibujar círculo de radio n cm ---
        if cmd == "circulo":
            r_cm = n
            segments = 36
            arc_length = 2 * math.pi * r_cm / segments
            move_delay = CM_DELAY_PER_CM * arc_length
            rot_delay_per_degree = COMMAND_DELAYS["R"] / 90
            angle_step = 360 / segments

            for _ in range(segments):
                try: requests.get(ROVER_URL, params={"State": "F"}, timeout=2)
                except: pass
                time.sleep(move_delay)
                try: requests.get(ROVER_URL, params={"State": "R"}, timeout=2)
                except: pass
                time.sleep(rot_delay_per_degree * angle_step)

            _send("S")
            continue

        # --- Dibujar cuadrado de lado n cm ---
        if cmd == "cuadrado":
            side_cm = n
            for _ in range(4):
                try: requests.get(ROVER_URL, params={"State": "F"}, timeout=2)
                except: pass
                time.sleep(CM_DELAY_PER_CM * abs(side_cm))
                try: requests.get(ROVER_URL, params={"State": "R"}, timeout=2)
                except: pass
                time.sleep(COMMAND_DELAYS["R"])
            _send("S")
            continue

        # --- Rotar sobre propio eje n vueltas (pivot) ---
        if cmd == "rotar":
            letter = "R" if n > 0 else "L"
            for _ in range(abs(n)):
                for _ in range(PULSES_PER_REV):
                    _send(letter)
                _send("S")
            continue

        # --- Caminar n pasos simulando pasos individuales ---
        if cmd == "caminar":
            letter = "F" if n > 0 else "B"
            for _ in range(abs(n)):
                _send(letter)  # mueve un "paso"
                _send("S")     # pausa entre pasos
            continue

        # --- Moonwalk n pasos al estilo MJ 🕺 ---
        if cmd == "moonwalk":
            # Para cada paso: desliza atrás y avanza con gracia
            back = "B" if n > 0 else "F"
            front = "F" if n > 0 else "B"
            for _ in range(abs(n)):
                _send(back)    # desliza hacia atrás
                _send("S")     # pequeña pausa de drama
                _send(front)   # avanza al estilo Moonwalk
                _send("S")     # aplausos
            continue

        # --- Avanzar centímetros reales ---
        if cmd == "avanzar_ctms":
            letter = "F" if n > 0 else "B"
            try: requests.get(ROVER_URL, params={"State": letter}, timeout=2)
            except: pass
            time.sleep(CM_DELAY_PER_CM * abs(n))
            _send("S")
            continue

        # --- Avanzar metros reales ---
        if cmd == "avanzar_mts":
            letter = "F" if n > 0 else "B"
            try: requests.get(ROVER_URL, params={"State": letter}, timeout=2)
            except: pass
            time.sleep(CM_DELAY_PER_CM * abs(n) * 100)
            _send("S")
            continue

        # --- Resto de comandos via translate() ---
        for letter in translate(cmd, n):
            _send(letter)
