from gpiozero import LED, Motor
from time import sleep

def test_motor():
    while True:
        # Input dall'utente per il modulo
        modulo = input("Seleziona il modulo da testare (W per modulo Ovest, E per modulo Est, Q per uscire): ").upper()

        if modulo == "Q":
            print("Uscita dal programma")
            break

        # Configurazione del modulo e motore
        if modulo == "E":
            led = LED(19)  # Pin GPIO per LED (abilita il modulo Est)
            motor = Motor(26, 13)  # Pin GPIO per controllare il motore Est
        elif modulo == "W":
            led = LED(16)  # Pin GPIO per LED (abilita il modulo Ovest)
            motor = Motor(20, 21)  # Pin GPIO per controllare il motore Ovest
        else:
            print("Modulo non valido. Riprovare.")
            continue

        # Accensione del LED (abilita il modulo)
        led.on()

        # Input per la direzione del motore
        verso = input("Seleziona la direzione (f per avanti, b per indietro, r per tornare al menu precedente): ").lower()

        if verso == "r":
            print("Tornando al menu del modulo...")
            led.off()
            continue

        # Controllo del verso del motore
        if verso == "b":
            print("Motore indietro")
            motor.backward()
        elif verso == "f":
            print("Motore avanti")
            motor.forward()
        else:
            print("Direzione non valida. Riprovare.")
            led.off()
            continue

        # Lascia il motore girare per 3 secondi
        sleep(3)

        # Spegne il LED e ferma il motore
        led.off()
        motor.stop()

        print("Test completato. Puoi selezionare un altro modulo o direzione.")

if __name__ == "__main__":
    test_motor()


