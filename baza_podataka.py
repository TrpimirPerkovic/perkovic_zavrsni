import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

PATH_BAZE = Path(__file__).parent / "mjerenja_senzora.db"
DANI_ZADRZAVANJA = 30

SHEMA = """
CREATE TABLE IF NOT EXISTS mjerenja (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vrijeme TEXT NOT NULL,
    temperatura REAL NOT NULL,
    vlaga REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS index_vrijeme ON mjerenja (vrijeme);
"""


class Baza:
    def __init__(self, putanja=PATH_BAZE):
        self._path = str(putanja)
        self._inicijalizacija()

    def _veza(self):
        veza = sqlite3.connect(self._path, timeout=10)
        veza.row_factory = sqlite3.Row
        return veza

    def _inicijalizacija(self):
        with self._veza() as veza:
            veza.executescript(SHEMA)
        logger.info("Baza spremna za rad: %s", self._path)

    def zapisi(self, temperatura, vlaga):
        vrijeme = datetime.now().isoformat(timespec="seconds")
        with self._veza() as veza:
            veza.execute(
                "INSERT INTO mjerenja (vrijeme, temperatura, vlaga) VALUES (?, ?, ?)",
                (vrijeme, temperatura, vlaga),
            )
        logger.debug("Zapisano: %.1f C, %.1f %%", temperatura, vlaga)

    def zadnja(self):
        with self._veza() as veza:
            red = veza.execute(
                "SELECT * FROM mjerenja ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return dict(red) if red else None

    def povijest(self, sati=24, limit=10000):
        granica = (datetime.now() - timedelta(hours=sati)).isoformat(timespec="seconds")
        with self._veza() as veza:
            redovi = veza.execute(
                "SELECT * FROM mjerenja WHERE vrijeme >= ? ORDER BY vrijeme ASC LIMIT ?",
                (granica, limit),
            ).fetchall()
        return [dict(red) for red in redovi]

    def statistika(self, sati=24):
        granica = (datetime.now() - timedelta(hours=sati)).isoformat(timespec="seconds")
        with self._veza() as veza:
            red = veza.execute(
                """SELECT COUNT(*) AS broj,
                          AVG(temperatura) AS temp_avg,
                          MIN(temperatura) AS temp_min,
                          MAX(temperatura) AS temp_max,
                          AVG(vlaga) AS vlaga_avg,
                          MIN(vlaga) AS vlaga_min,
                          MAX(vlaga) AS vlaga_max
                   FROM mjerenja WHERE vrijeme >= ?""",
                (granica,),
            ).fetchone()
        return dict(red) if red else None

    def ocisti_povijest(self, dani=DANI_ZADRZAVANJA):
        granica = (datetime.now() - timedelta(days=dani)).isoformat(timespec="seconds")
        with self._veza() as veza:
            kursor = veza.execute("DELETE FROM mjerenja WHERE vrijeme < ?", (granica,))
            obrisano = kursor.rowcount
        if obrisano:
            logger.info("Obrisano %d starih zapisa", obrisano)
        return obrisano


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    baza = Baza()
    baza.zapisi(25.9, 80.0)
    baza.zapisi(26.0, 79.0)
    baza.zapisi(26.3, 81.0)
    print("Zadnje:", baza.zadnja())
    print("Statistika:", baza.statistika())
    print("Broj u povijesti:", len(baza.povijest()))
