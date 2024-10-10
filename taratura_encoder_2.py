import lgpio
from gpiozero import Button
from time import sleep

# Definizione dei GPIO per i pulsanti di finecorsa
curtain_W_verify_open = Button(5)
curtain_W_verify_closed = Button(6)
curtain_E_verify_open = Button(22)
curtain_E_verify_closed = Button(12)

# Definizione dei GPIO per gli encoder
clk_encoder_est = 18
dt_encoder_est = 23
clk_encoder_west = 24
dt_encoder_west = 25

# Setup GPIO con lgpio
chip = lgpio.gpiochip_open(0)

# Configurazione dei pin degli encoder come input
lgpio.gpio_claim_input(chip, clk_encoder_est)
lgpio.gpio_claim_input(chip, dt_encoder_est)
lgpio.gpio_claim_input(chip, clk_encoder_west)
lgpio.gpio_claim_input(chip, dt_encoder_west)

# Variabili per il conteggio degli impulsi dell'encoder
encoder_count_west = 0
encoder_count_est = 0
counting_west = False
counting_est = False

# Funzione per gestire il conteggio dell'encoder Ovest
def count_west_encoder(chip, gpio, level, tick):
    print("mario_west")
    global encoder_count_west, counting_west
    print(f"[DEBUG] Callback encoder Ovest chiamato - GPIO: {gpio}, Livello: {level}, Tick: {tick}")

    if counting_west:
        clk_state = lgpio.gpio_read(chip, clk_encoder_west)
        dt_state = lgpio.gpio_read(chip, dt_encoder_west)
        print(f"[DEBUG] Stato encoder Ovest - CLK: {clk_state}, DT: {dt_state}")

        if clk_state == dt_state:
            encoder_count_west += 1  # Rotazione in un verso
        else:
            encoder_count_west -= 1  # Rotazione nel verso opposto
        print(f"Encoder West Count: {encoder_count_west}")

# Funzione per gestire il conteggio dell'encoder Est
def count_est_encoder(chip, gpio, level, tick):
    print("mario_est")
    global encoder_count_est, counting_est
    print(f"[DEBUG] Callback encoder Est chiamato - GPIO: {gpio}, Livello: {level}, Tick: {tick}")

    if counting_est:
        clk_state = lgpio.gpio_read(chip, clk_encoder_est)
        dt_state = lgpio.gpio_read(chip, dt_encoder_est)
        print(f"[DEBUG] Stato encoder Est - CLK: {clk_state}, DT: {dt_state}")

        if clk_state == dt_state:
            encoder_count_est += 1  # Rotazione in un verso
        else:
            encoder_count_est -= 1  # Rotazione nel verso opposto
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

# Stato intermedio delle tende in movimento
def check_movement_status():
    if not curtain_W_verify_closed.is_pressed and not curtain_W_verify_open.is_pressed:
        print("[DEBUG] Tenda Ovest in fase di apertura...")
    if not curtain_E_verify_closed.is_pressed and not curtain_E_verify_open.is_pressed:
        print("[DEBUG] Tenda Est in fase di apertura...")

# Collegamento delle funzioni di callback agli eventi di pressione del pulsante
curtain_W_verify_closed.when_released = handle_west_closed_released
curtain_W_verify_open.when_pressed = handle_west_open
curtain_E_verify_closed.when_released = handle_est_closed_released
curtain_E_verify_open.when_pressed = handle_est_open

# Collegamento del conteggio encoder ai cambiamenti del segnale di clock (rising edge)
west_callback_id = lgpio.callback(chip, clk_encoder_west, lgpio.BOTH_EDGES, count_west_encoder)
est_callback_id = lgpio.callback(chip, clk_encoder_est, lgpio.BOTH_EDGES, count_est_encoder)

# Stampa di conferma che il callback è stato registrato
print(f"[DEBUG] Callback encoder Ovest registrato con ID: {west_callback_id}")
print(f"[DEBUG] Callback encoder Est registrato con ID: {est_callback_id}")

# Polling diretto per verificare i cambiamenti di stato del GPIO (debug manuale)
try:
    while True:
        # Controlla lo stato dei pin clk manualmente per verificare eventuali cambiamenti
        clk_west_state = lgpio.gpio_read(chip, clk_encoder_west)
        clk_est_state = lgpio.gpio_read(chip, clk_encoder_est)
        print(f"[DEBUG] Polling Manuale - CLK West: {clk_west_state}, CLK Est: {clk_est_state}")
        
        check_movement_status()
        sleep(0.05)  # Controlla lo stato ogni 0.5 secondi
except KeyboardInterrupt:
    print("[DEBUG] Programma terminato manualmente")
finally:
    lgpio.gpiochip_close(chip)  # Pulisce la configurazione dei GPIO alla fine del programma
