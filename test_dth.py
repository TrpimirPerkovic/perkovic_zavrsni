import time
import board
import adafruit_dht

dht = adafruit_dht.DHT11(board.D4)

while True:
    try:
        temp = dht.temperature
        hum = dht.humidity
        print(f"Temperatura: {temp}°C   Vlaga: {hum}%")
    except RuntimeError as e:
        print(f"Greska ocitanja: {e}")
    except Exception as e:
        dht.exit()
        raise e
    time.sleep(2.0)

