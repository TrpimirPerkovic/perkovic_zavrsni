import time
import logging
import board 
import adafruit_dht

logger = logging.getLogger(__name__)

#granice prema specifikaciji

TEMP_MIN, TEMP_MAX = -10.0, 60.0
VLAGA_MIN, VLAGA_MAX = 5.0, 95.0

BROJ_POKUSAJA = 3
PAUZA_POKUSAJA = 2.5

class DHT11Senzor:
	def __init__(self, pin=board.D4):
		self._uredaj = adafruit_dht.DHT11(pin)
		self._zagrijan = False
	
	def _sirovo_ocitanje(self):
		temp = self._uredaj.temperature
		vlaga = self._uredaj.humidity
		if temp is None or vlaga is None:
			raise RuntimeError("Senzor vraća prazno očitanje")
		return float(temp), float(vlaga)

	def _valjanoOcitanje(self, temp, vlaga):
		return TEMP_MIN <= temp <= TEMP_MAX and VLAGA_MIN <= vlaga <= VLAGA_MAX
	
	def ocitaj(self):
	# vraća temp + vlaga ili None ako pokusaji padnu
		if not self._zagrijan:
			try:
				self._sirovo_ocitanje()
			except Exception:
				pass
			self._zagrijan = True
			time.sleep(PAUZA_POKUSAJA)

		for pokusaj in range(1, BROJ_POKUSAJA + 1):
			try:
				temp, vlaga = self._sirovo_ocitanje()
				if self._valjanoOcitanje(temp, vlaga):
					return temp, vlaga
				logger.warning("Očitanje van granice: %.1f C, %.1f %%", temp, vlaga)
			except RuntimeError as e:
				logger.debug("Pokušaj %d neuspješan: %s", pokusaj, e)
			if pokusaj < BROJ_POKUSAJA:
				time.sleep(PAUZA_POKUSAJA)

				
		logger.error("Sva %d pokušaja neuspješna", BROJ_POKUSAJA)
		return None

	def zatvori(self):
		self._uredaj.exit()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    senzor = DHT11Senzor()
    try:
        for i in range(20):
            rezultat = senzor.ocitaj()
            if rezultat:
                print(f"{i+1}. {rezultat[0]:.1f} C   {rezultat[1]:.1f} %")
            else:
                print(f"{i+1}. NEUSPJEH")
            time.sleep(3)
    finally:
        senzor.zatvori()				
















 
