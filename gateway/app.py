from flask import Flask, Response
import requests

app = Flask(__name__)

# Ruta para obtener datos de sentimiento
@app.route("/sentiment", methods=["GET"])
def get_sentiment():
    r = requests.get("http://sentiment:5000/sentiment-data")
    return Response(r.content, mimetype='application/json')

# Ruta para procesar datos
@app.route("/process", methods=["GET"])
def get_process():
    r = requests.get("http://process:5000/proccess-data")
    return Response(r.content, mimetype='application/json')

# Ruta para datos de mercado
@app.route("/market", methods=["GET"])
def get_market():
    r = requests.get("http://marketdata:5000/download-market-data")
    return Response(r.content, mimetype='application/json')

# Ruta para construir portafolio
@app.route("/portfolio", methods=["GET"])
def get_portfolio():
    r = requests.get("http://portfolio:5000/build-portfolio")
    return Response(r.content, mimetype='application/json')

# Ruta para graficar
@app.route("/plot", methods=["GET"])
def get_plot():
    r = requests.get("http://plot:5000/plot", stream=True)
    return Response(r.content, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)