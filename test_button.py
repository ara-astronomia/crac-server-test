from gpiozero import Button

# Definizione dei GPIO per i pulsanti
curtain_W_verify_open = Button(5)  # pin 35 per finecorsa tenda Ovest aperta
curtain_W_verify_closed = Button(6)  # pin 37 per finecorsa tenda Ovest chiusa
curtain_E_verify_open = Button(22)  # pin 15 per finecorsa tenda Est aperta
curtain_E_verify_closed = Button(12)  # pin 32 per finecorsa tenda Est chiusa

# Definizione delle funzioni di callback per ciascun pulsante
def handle_west_open():
    print("Finecorsa apertura tenda Ovest")

def handle_west_closed():
    print("Finecorsa chiusura tenda Ovest")

def handle_east_open():
    print("Finecorsa apertura tenda Est")

def handle_east_closed():
    print("Finecorsa chiusura tenda Est")

# Collegamento delle funzioni di callback agli eventi di pressione del pulsante
curtain_W_verify_open.when_pressed = handle_west_open
curtain_W_verify_closed.when_pressed = handle_west_closed
curtain_E_verify_open.when_pressed = handle_east_open
curtain_E_verify_closed.when_pressed = handle_east_closed

# Mantiene il programma in esecuzione per attendere gli eventi dei pulsanti
from signal import pause
pause()

