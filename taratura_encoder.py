from gpiozero import Button
from time import sleep

# Definizione dei GPIO per i pulsanti di finecorsa
curtain_W_verify_open = Button(5)  # pin 35 per finecorsa tenda Ovest aperta
curtain_W_verify_closed = Button(6)  # pin 37 per finecorsa tenda Ovest chiusa
curtain_E_verify_open = Button(22)  # pin 15 per finecorsa tenda Est aperta
curtain_E_verify_closed = Button(12)  # pin 32 per finecorsa tenda Est chiusa

# Definizione dei GPIO per gli encoder
clk_encoder_est = Button(18, pull_up=True)
dt_encoder_est = Button(23, pull_up=True)
clk_encoder_west = Button(24, pull_up=True)
dt_encoder_west = Button(25, pull_up=True)

# Variabili per il conteggio degli impulsi dell'encoder
encoder_count_west = 0
encoder_count_est = 0
counting_west = False
counting_est = False

# Funzione per gestire il conteggio dell'encoder Ovest
def count_west_encoder():
    global encoder_count_west, counting_west
    if counting_west:
        if dt_encoder_west.is_pressed:
            encoder_count_west -= 1  # Rotazione in un verso
        else:
            encoder_count_west += 1  # Rotazione nell'altro verso
        print(f"Encoder West Count: {encoder_count_west}")

# Funzione per gestire il conteggio dell'encoder Est
def count_est_encoder():
    global encoder_count_est, counting_est
    if counting_est:
        if dt_encoder_est.is_pressed:
            encoder_count_est -= 1  # Rotazione in un verso
        else:
            encoder_count_est += 1  # Rotazione nell'altro verso
        print(f"Encoder Est Count: {encoder_count_est}")

# Funzioni di callback per i pulsanti di finecorsa
def handle_west_closed_released():
    global counting_west, encoder_count_west
    counting_west = True
    encoder_count_west = 0
    print("[DEBUG] Inizio conteggio encoder per tenda Ovest")

def handle_west_open():
    global counting_west
    counting_west = False
    print(f"[DEBUG] Fine conteggio encoder per tenda Ovest. Conteggio finale: {encoder_count_west}")

def handle_est_closed_released():
    global counting_est, encoder_count_est
    counting_est = True
    encoder_count_est = 0
    print("[DEBUG] Inizio conteggio encoder per tenda Est")

def handle_est_open():
    global counting_est
    counting_est = False
    print(f"[DEBUG] Fine conteggio encoder per tenda Est. Conteggio finale: {encoder_count_est}")

# Collegamento delle funzioni di callback agli eventi di pressione del pulsante di finecorsa
curtain_W_verify_closed.when_released = handle_west_closed_released
curtain_W_verify_open.when_pressed = handle_west_open
curtain_E_verify_closed.when_released = handle_est_closed_released
curtain_E_verify_open.when_pressed = handle_est_open

# Collegamento delle funzioni di callback per il conteggio degli encoder
clk_encoder_west.when_pressed = count_west_encoder
clk_encoder_est.when_pressed = count_est_encoder

# Mantiene il programma in esecuzione per attendere gli eventi dei pulsanti e degli encoder
try:
    while True:
        sleep(0.1)  # Attendi per ridurre il carico della CPU
except KeyboardInterrupt:
    print("[DEBUG] Programma terminato manualmente")
