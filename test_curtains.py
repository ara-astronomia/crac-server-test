"""
test_crac.py
Script di test per motori, encoder, finecorsa delle tende e tetto.
Pin in modalità BCM, coerenti con config.ini del server.

Sicurezze implementate:
- Il tetto non può aprirsi se è già aperto
- Il tetto non può chiudersi se le tende non sono chiuse
"""

from gpiozero import Button, LED, Motor, OutputDevice
from time import sleep
from signal import pause
import threading

# =============================================================================
# PIN GPIO (BCM) — coerenti con config.ini
# =============================================================================

# Finecorsa
PIN_W_VERIFY_OPEN   = 19  # pin fisico 35 - finecorsa tenda Ovest aperta
PIN_W_VERIFY_CLOSED = 26  # pin fisico 37 - finecorsa tenda Ovest chiusa
PIN_E_VERIFY_OPEN   =  8  # pin fisico 15 - finecorsa tenda Est aperta
PIN_E_VERIFY_CLOSED =  7  # pin fisico 32 - finecorsa tenda Est chiusa

# Encoder
PIN_CLK_EAST = 18  # pin fisico 12
PIN_DT_EAST  = 23  # pin fisico 16
PIN_CLK_WEST = 24  # pin fisico 18
PIN_DT_WEST  = 25  # pin fisico 22

# Motori
PIN_MOTOR_E_FORWARD  = 13  # motorE_B
PIN_MOTOR_E_BACKWARD =  6  # motorE_A
PIN_MOTOR_E_ENABLE   =  5  # motorE_E

PIN_MOTOR_W_FORWARD  = 21  # motorW_B
PIN_MOTOR_W_BACKWARD = 20  # motorW_A
PIN_MOTOR_W_ENABLE   = 16  # motorW_E

# Tetto
PIN_ROOF_VERIFY_CLOSED = 27  # pin fisico 11 - finecorsa tetto chiuso
PIN_ROOF_VERIFY_OPEN   = 17  # pin fisico 7  - finecorsa tetto aperto
PIN_ROOF_SWITCH        =  4  # pin fisico 13 - comando apertura/chiusura tetto

# =============================================================================
# STATO ENCODER
# =============================================================================
encoder_count = {'E': 0, 'W': 0}
encoder_active = {'E': False, 'W': False}

# =============================================================================
# FINECORSA
# =============================================================================
curtain_W_verify_open   = Button(PIN_W_VERIFY_OPEN,   pull_up=True)
curtain_W_verify_closed = Button(PIN_W_VERIFY_CLOSED, pull_up=True)
curtain_E_verify_open   = Button(PIN_E_VERIFY_OPEN,   pull_up=True)
curtain_E_verify_closed = Button(PIN_E_VERIFY_CLOSED, pull_up=True)

# Tetto
roof_verify_closed = Button(PIN_ROOF_VERIFY_CLOSED, pull_up=True)
roof_verify_open   = Button(PIN_ROOF_VERIFY_OPEN,   pull_up=True)
roof_switch        = OutputDevice(PIN_ROOF_SWITCH)

# Encoder
clk_east = Button(PIN_CLK_EAST, pull_up=True)
dt_east  = Button(PIN_DT_EAST,  pull_up=True)
clk_west = Button(PIN_CLK_WEST, pull_up=True)
dt_west  = Button(PIN_DT_WEST,  pull_up=True)

# =============================================================================
# CALLBACK FINECORSA
# =============================================================================
def handle_E_closed_pressed():
    print("[EST] Finecorsa CHIUSURA premuto")
    encoder_active['E'] = False

def handle_E_closed_released():
    print("[EST] Finecorsa CHIUSURA rilasciato → inizio conteggio encoder")
    encoder_count['E'] = 0
    encoder_active['E'] = True

def handle_E_open_pressed():
    print(f"[EST] Finecorsa APERTURA premuto → conteggio finale: {encoder_count['E']}")
    encoder_active['E'] = False

def handle_E_open_released():
    print("[EST] Finecorsa APERTURA rilasciato")

def handle_W_closed_pressed():
    print("[OVEST] Finecorsa CHIUSURA premuto")
    encoder_active['W'] = False

def handle_W_closed_released():
    print("[OVEST] Finecorsa CHIUSURA rilasciato → inizio conteggio encoder")
    encoder_count['W'] = 0
    encoder_active['W'] = True

def handle_W_open_pressed():
    print(f"[OVEST] Finecorsa APERTURA premuto → conteggio finale: {encoder_count['W']}")
    encoder_active['W'] = False

def handle_W_open_released():
    print("[OVEST] Finecorsa APERTURA rilasciato")

curtain_E_verify_closed.when_pressed  = handle_E_closed_pressed
curtain_E_verify_closed.when_released = handle_E_closed_released
curtain_E_verify_open.when_pressed    = handle_E_open_pressed
curtain_E_verify_open.when_released   = handle_E_open_released

curtain_W_verify_closed.when_pressed  = handle_W_closed_pressed
curtain_W_verify_closed.when_released = handle_W_closed_released
curtain_W_verify_open.when_pressed    = handle_W_open_pressed
curtain_W_verify_open.when_released   = handle_W_open_released

# =============================================================================
# CALLBACK ENCODER
# =============================================================================
def count_east():
    if encoder_active['E']:
        encoder_count['E'] += -1 if dt_east.is_pressed else 1
        print(f"[EST]   Encoder: {encoder_count['E']}")

def count_west():
    if encoder_active['W']:
        encoder_count['W'] += -1 if dt_west.is_pressed else 1
        print(f"[OVEST] Encoder: {encoder_count['W']}")

clk_east.when_pressed = count_east
clk_west.when_pressed = count_west

# =============================================================================
# TEST MOTORI
# =============================================================================
def test_motor():
    while True:
        modulo = input("\nSeleziona tenda (E=Est, W=Ovest, Q=esci): ").upper()
        if modulo == 'Q':
            break
        if modulo not in ('E', 'W'):
            print("Tenda non valida.")
            continue

        if modulo == 'E':
            enable = LED(PIN_MOTOR_E_ENABLE)
            motor  = Motor(PIN_MOTOR_E_FORWARD, PIN_MOTOR_E_BACKWARD)
        else:
            enable = LED(PIN_MOTOR_W_ENABLE)
            motor  = Motor(PIN_MOTOR_W_FORWARD, PIN_MOTOR_W_BACKWARD)

        verso = input("Direzione (f=avanti, b=indietro, r=torna): ").lower()
        if verso == 'r':
            continue
        if verso not in ('f', 'b'):
            print("Direzione non valida.")
            continue

        enable.on()
        if verso == 'f':
            print(f"[{modulo}] Motore avanti. Premi H per fermare.")
            motor.forward()
        else:
            print(f"[{modulo}] Motore indietro. Premi H per fermare.")
            motor.backward()

        while True:
            cmd = input("").upper()
            if cmd == 'H':
                motor.stop()
                enable.off()
                print(f"[{modulo}] Motore fermato.")
                break
            else:
                print("Premi H per fermare il motore.")

# =============================================================================
# MENU PRINCIPALE
# =============================================================================
ROOF_TIMEOUT_OPEN  = 50
ROOF_TIMEOUT_CLOSE = 90

def print_status():
    print("\n=== STATO GPIO ===")
    print(f"  [TETTO] chiuso  : {roof_verify_closed.is_pressed}")
    print(f"  [TETTO] aperto  : {roof_verify_open.is_pressed}")
    print(f"  [EST]   chiusa  : {curtain_E_verify_closed.is_pressed}")
    print(f"  [EST]   aperta  : {curtain_E_verify_open.is_pressed}")
    print(f"  [OVEST] chiusa  : {curtain_W_verify_closed.is_pressed}")
    print(f"  [OVEST] aperta  : {curtain_W_verify_open.is_pressed}")
    print("==================\n")

def roof_open():
    if roof_verify_open.is_pressed:
        print("[TETTO] Già aperto.")
        return
    print("[TETTO] Apertura in corso...")
    roof_switch.on()
    elapsed = 0
    while not roof_verify_open.is_pressed and elapsed < ROOF_TIMEOUT_OPEN:
        sleep(1)
        elapsed += 1
        print(f"[TETTO] Attendo apertura... ({elapsed}s)")
    if roof_verify_open.is_pressed:
        print("[TETTO] ✓ Tetto aperto.")
    else:
        print("[TETTO] ✗ TIMEOUT — tetto non ha raggiunto la posizione aperta!")

def roof_close():
    if roof_verify_closed.is_pressed:
        print("[TETTO] Già chiuso.")
        return
    if not curtain_E_verify_closed.is_pressed or not curtain_W_verify_closed.is_pressed:
        print("[TETTO] ⚠️  BLOCCO — tende non chiuse! Impossibile chiudere il tetto.")
        return
    print("[TETTO] Chiusura in corso...")
    roof_switch.off()
    elapsed = 0
    while not roof_verify_closed.is_pressed and elapsed < ROOF_TIMEOUT_CLOSE:
        sleep(1)
        elapsed += 1
        print(f"[TETTO] Attendo chiusura... ({elapsed}s)")
    if roof_verify_closed.is_pressed:
        print("[TETTO] ✓ Tetto chiuso.")
    else:
        print("[TETTO] ✗ TIMEOUT — tetto non ha raggiunto la posizione chiusa!")

def main():
    print_status()
    while True:
        print("\n=== MENU TEST CRAC ===")
        print("  S - Stato GPIO")
        print("  A - Apri tetto")
        print("  C - Chiudi tetto  [sicurezza: tende devono essere chiuse]")
        print("  M - Test motore tenda  [tetto deve essere aperto]")
        print("  E - Monitor encoder e finecorsa  [Ctrl+C per tornare]")
        print("  Q - Esci")
        scelta = input("\nScelta: ").upper()

        if scelta == 'S':
            print_status()

        elif scelta == 'A':
            roof_open()

        elif scelta == 'C':
            roof_close()

        elif scelta == 'M':
            if not roof_verify_open.is_pressed:
                print("⚠️  Il tetto non è aperto! Apri il tetto prima di testare i motori.")
            else:
                test_motor()

        elif scelta == 'E':
            print("\nMonitor attivo — aziona manualmente le tende. Ctrl+C per tornare al menu.")
            try:
                pause()
            except KeyboardInterrupt:
                print("\nMonitor interrotto.")

        elif scelta == 'Q':
            print("Uscita.")
            break

        else:
            print("Scelta non valida.")

if __name__ == "__main__":
    main()