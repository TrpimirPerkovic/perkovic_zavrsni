""" API za pristup mjerenjima """

import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from baza_podataka import Baza
from servis import servisMjerenja

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)
baza = Baza()
servis = servisMjerenja()


@app.route("/")
def pocetna():
    return app.send_static_file("index.html")

@app.route('/api/trenutno')
def trenutno():
    mjerenje = baza.zadnja()
    if mjerenje is None:
        return jsonify({"greska ": "Nema mjerenja"}), 404
    return jsonify(mjerenje)

@app.route("/api/povijest")
def povijest():
    try:
        sati = int(request.args.get("sati", 24))
    except ValueError:
        return jsonify({"greska ": " Param. 'sati' mora biti cijeli broj"}), 400
    
    if not 1 <= sati <= 720:
        return jsonify({"greska ": "Param, 'sati' mora biti >= 1 i <= 720"}), 400
    
    podaci = baza.povijest(sati=sati)
    return jsonify({"sati": sati, "broj": len(podaci), "mjerenja": podaci})

@app.route("/api/statistika")
def statistika():
    try:
        sati = int(request.args.get("sati", 24))
    except ValueError:
        return jsonify({"greska": "Param. sati mora biti cijewli broj"}), 400
    
    if not 1 <= sati <= 720:
        return jsonify({"greska": "Param. 'sati' mora biti >= 1 i <= 720"})
    
    return jsonify(baza.statistika(sati=sati))

@app.route("/api/stanje")
def stanje():
    return jsonify(servis.stanje())

@app.errorhandler(404)
def nijePronadeno(e):
    return jsonify({"greska": "Path nije pronađen"}), 400

if __name__ == "__main__":
    servis.pokreni()
    try:
        app.run(host="0.0.0.0", port=5000, debug = False, threaded=True)
    finally:
        servis.zaustavi()
