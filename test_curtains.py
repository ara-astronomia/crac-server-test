"""
test_crac.py
Script di test per motori, encoder, finecorsa delle tende e tetto.
Pin in modalità BCM, coerenti con config.ini del server.

Sicurezze implementate:
- Il tetto non può aprirsi se è già aperto
- Il tetto non può chiudersi se le tende non sono chiuse
- I motori delle tende non possono essere testati se il tetto è chiuso
"""

from gpiozero import Button, RotaryEncoder, Motor, OutputDevice
from time import sleep
from signal import pause
import threading

# =============================================================================
# PIN GPIO (BCM) — coerenti con config.ini
# =============================================================================

# Finecorsa tende
PIN_W_VERIFY_OPEN   = 19  # pin fisico 35 - finecorsa tenda Ovest aperta
PIN_W_VERIFY_CLOSED = 26  # pin fisico 37 - finecorsa tenda Ovest chiusa
PIN_E_VERIFY_OPEN   =  8  # pin fisico 15 - finecorsa tenda Est aperta
PIN_E_VERIFY_CLOSED =  7  # pin fisico 32 - finecorsa tenda Est chiusa

# Encoder
PIN_CLK_EAST = 18  # pin fisico 12
PIN_DT_EAST  = 23  # pin fisico 16
PIN_CLK_WEST = 24  # pin fisico 18
PIN_DT_WEST  = 25  # pin fisico 22

# Motori tende
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
# TIMEOUT TETTO
# =============================================================================
ROOF_TIMEOUT_OPEN  = 50   # secondi
ROOF_TIMEOUT_CLOSE = 90   # secondi — include il ritardo del relay

# =============================================================================
# FINECORSA
# =============================================================================
curtain_W_verify_open   = Button(PIN_W_VERIFY_OPEN,   pull_up=True)
curtain_W_verify_closed = Button(PIN_W_VERIFY_CLOSED, pull_up=True, bounce_time=0.1)
curtain_E_verify_open   = Button(PIN_E_VERIFY_OPEN,   pull_up=True)
curtain_E_verify_closed = Button(PIN_E_VERIFY_CLOSED, pull_up=True, bounce_time=0.1)

# Tetto
roof_verify_closed = Button(PIN_ROOF_VERIFY_CLOSED, pull_up=True)
roof_verify_open   = Button(PIN_ROOF_VERIFY_OPEN,   pull_up=True)
roof_switch        = OutputDevice(PIN_ROOF_SWITCH)

# Encoder
encoder_E = RotaryEncoder(PIN_CLK_EAST, PIN_DT_EAST, max_steps=205)
encoder_W = RotaryEncoder(PIN_CLK_WEST, PIN_DT_WEST, max_steps=205)

# =============================================================================
# CALLBACK FINECORSA
# =============================================================================
def handle_E_closed_pressed():
    print("[EST] Finecorsa CHIUSURA premuto")

def handle_E_closed_released():
    print("[EST] Finecorsa CHIUSURA rilasciato")

def handle_E_open_pressed():
    print(f"[EST] Finecorsa APERTURA premuto — steps encoder: {encoder_E.steps}")

def handle_E_open_released():
    print("[EST] Finecorsa APERTURA rilasciato")

def handle_W_closed_pressed():
    print("[OVEST] Finecorsa CHIUSURA premuto")

def handle_W_closed_released():
    print("[OVEST] Finecorsa CHIUSURA rilasciato")

def handle_W_open_pressed():
    print(f"[OVEST] Finecorsa APERTURA premuto — steps encoder: {encoder_W.steps}")

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
    print(f"[EST]   Encoder: {encoder_E.steps}")

def count_west():
    print(f"[OVEST] Encoder: {encoder_W.steps}")

encoder_E.when_rotated = count_east
encoder_W.when_rotated = count_west

# =============================================================================
# TEST MOTORI
# =============================================================================
def wait_for_halt(motor, modulo):
    """Thread separato per attendere H senza bloccare i print dell'encoder."""
    while True:
        try:
            cmd = input("").strip().upper()
            if cmd == 'H':
                motor.stop()
                motor.enable_device.off()
                motor.close()
                print(f"[{modulo}] Motore fermato.")
                break
        except UnicodeDecodeError:
            print("Carattere non valido, premi H per fermare.")
            continue

def test_motor():
    while True:
        try:
            modulo = input("\nSeleziona tenda (E=Est, W=Ovest, Q=esci): ").strip().upper()
        except UnicodeDecodeError:
            print("Carattere non valido, riprova.")
            continue

        if modulo == 'Q':
            break
        if modulo not in ('E', 'W'):
            print("Tenda non valida.")
            continue

        if modulo == 'E':
            motor = Motor(
                forward=PIN_MOTOR_E_FORWARD,
                backward=PIN_MOTOR_E_BACKWARD,
                enable=PIN_MOTOR_E_ENABLE,
                pwm=False
            )
        else:
            motor = Motor(
                forward=PIN_MOTOR_W_FORWARD,
                backward=PIN_MOTOR_W_BACKWARD,
                enable=PIN_MOTOR_W_ENABLE,
                pwm=False
            )

        try:
            verso = input("Direzione (f=avanti, b=indietro, r=torna): ").strip().lower()
        except UnicodeDecodeError:
            print("Carattere non valido, riprova.")
            motor.close()
            continue

        if verso == 'r':
            motor.close()
            continue
        if verso not in ('f', 'b'):
            print("Direzione non valida.")
            motor.close()
            continue

        motor.enable_device.on()
        print(f"[{modulo}] enable_device.value: {motor.enable_device.value}")
        if verso == 'f':
            motor.forward()
        else:
            motor.backward()

        print(f"[{modulo}] motor.value: {motor.value}")
        print(f"[{modulo}] Motore avviato. Premi H per fermare.")

        # Thread separato — i print dell'encoder continuano mentre aspetti H
        halt_thread = threading.Thread(target=wait_for_halt, args=(motor, modulo), daemon=True)
        halt_thread.start()
        halt_thread.join()

# =============================================================================
# TETTO
# =============================================================================
def roof_open():
    if roof_verify_open.is_pressed:
        print("[TETTO] Già aperto.")
        return
    print("[TETTO] Apertura in corso...")
    roof_switch.on()  # resta ON finché non chiudiamo
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
    roof_switch.off()  # OFF → parte il delay → tetto si chiude
    elapsed = 0
    while not roof_verify_closed.is_pressed and elapsed < ROOF_TIMEOUT_CLOSE:
        sleep(1)
        elapsed += 1
        print(f"[TETTO] Attendo chiusura... ({elapsed}s)")
    if roof_verify_closed.is_pressed:
        print("[TETTO] ✓ Tetto chiuso.")
    else:
        print("[TETTO] ✗ TIMEOUT — tetto non ha raggiunto la posizione chiusa!")

# =============================================================================
# STATO GPIO
# =============================================================================
def print_status():
    print("\n=== STATO GPIO ===")
    print(f"  [TETTO] chiuso  : {roof_verify_closed.is_pressed}")
    print(f"  [TETTO] aperto  : {roof_verify_open.is_pressed}")
    print(f"  [EST]   chiusa  : {curtain_E_verify_closed.is_pressed}")
    print(f"  [EST]   aperta  : {curtain_E_verify_open.is_pressed}")
    print(f"  [EST]   encoder : {encoder_E.steps}")
    print(f"  [OVEST] chiusa  : {curtain_W_verify_closed.is_pressed}")
    print(f"  [OVEST] aperta  : {curtain_W_verify_open.is_pressed}")
    print(f"  [OVEST] encoder : {encoder_W.steps}")
    print("==================\n")

# =============================================================================
# MENU PRINCIPALE
# =============================================================================
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

        try:
            scelta = input("\nScelta: ").strip().upper()
        except UnicodeDecodeError:
            print("Carattere non valido, riprova.")
            continue

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