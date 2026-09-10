""" Servis očitavanja senzora i zapisivanja u bazu """

import time
import logging
import threading
from datetime import datetime, date
from sensor import DHT11Senzor
from baza_podataka import Baza

logger = logging.getLogger(__name__)
INTERVAL_MJERENJA = 60
SAT_CISCENJA = 3

class servisMjerenja:
    def __init__(self, interval = INTERVAL_MJERENJA):
        self._interval = interval
        self._senzor = DHT11Senzor()
        self._baza = Baza()
        self._radi = False
        self._dretva = None
        self._zadnjeCiscenje = None
        self._broj_uspjesnih_pokusaja = 0
        self._broj_neuspjesnih_pokusaja = 0

    def _moguce_ciscenje(self):
        danas=date.today()
        if self._zadnjeCiscenje == danas:
            return
        if datetime.now().hour < SAT_CISCENJA:
            return
        self._baza.ocisti_povijest()
        self._zadnjeCiscenje = danas

    def _jedan_ciklus(self):
        rezultat = self._senzor.ocitaj()
        if rezultat is None:
            self._broj_neuspjesnih_pokusaja += 1
            logger.warning("Mjerenje je neuspješno (ukupno: %d)", self._broj_neuspjesnih_pokusaja)
            return
        temperatura, vlaga = rezultat
        self._baza.zapisi(temperatura, vlaga)
        self._broj_uspjesnih_pokusaja += 1
        logger.info("Mjerenje %d: %.1f C, %.1f %%", self._broj_uspjesnih_pokusaja, temperatura, vlaga)

    def _petlja(self):
        logger.info("Servis je pokrenut: interval %d s", self._interval)
        while self._radi:
            pocetak = time.monotonic()
            try:
                self._jedan_ciklus()
                self._moguce_ciscenje()
            except Exception as e:
                logger.exception("Greška u ciklusu čišćenja/mjerenja: %s", e)
            proteklo = time.monotonic() - pocetak
            preostalo = max(0.0, self._interval - proteklo)
            kraj = time.monotonic() + preostalo
            while self._radi and time.monotonic() < kraj:
                time.sleep(0.5)
            logger.info("Servis stopiran")

    def pokreni(self):
        if self._radi:
            return
        self._radi = True
        self._dretva = threading.Thread(target = self._petlja, daemon=True)
        self._dretva.start()

    def zaustavi(self):
        self._radi = False
        if self._dretva:
            self._dretva.join(timeout=5)
        self._senzor.zatvori()

    def stanje(self):
        ukupno = self._broj_uspjesnih_pokusaja + self._broj_neuspjesnih_pokusaja
        postotak = (self._broj_neuspjesnih_pokusaja / ukupno * 100) if ukupno else 0.0
        return {
            "radi": self._radi,
            "interval": self._interval,
            "uspjesnih": self._broj_uspjesnih_pokusaja,
            "neuspjesnih": self._broj_neuspjesnih_pokusaja,
            "postotak_gresaka": round(postotak, 3),
}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s")
    servis = servisMjerenja(interval=5)
    servis.pokreni()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n")
        print("Zaustavljanje")
        servis.zaustavi()
        print("Stanje: ", servis.stanje())

