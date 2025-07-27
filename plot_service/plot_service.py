import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick 
from flask import Flask, jsonify, Response, send_file
import requests

app = Flask(__name__)
matplotlib.use('Agg') # nuevo (# Para poder graficar sin interfaz)
plt.style.use('ggplot')

#Get the portfolio of 'portfolio_service' microservice  
def get_portfolio_df(): 
   datosEnJson = requests.get("http://portfolio:5000/build-portfolio")
   portfolio_df = pd.read_json(datosEnJson.text)
   print(portfolio_df.head)
   print(portfolio_df.columns)
   return portfolio_df

#Plot (graficar) the two columns of the portfolio in a graph
def plotPortfolio(portfolio_dff):
   portfolios_cumulative_return = np.exp(np.log1p(portfolio_dff).cumsum()).sub(1)
   portfolios_cumulative_return.plot(figsize=(16,6))
   plt.title('Twitter Engagement Ratio Strategy Return Over Time')
   plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1))
   plt.ylabel('Return')
   plt.savefig("retorno_estrategia.png")
   plt.close()
   return "retorno_estrategia.png"

#Define the endpoint to plot the portfolio 
@app.route("/plot", methods=["GET"])
def plot():
   try:
       portfolio = get_portfolio_df()
       imagen = plotPortfolio(portfolio)
       return send_file(imagen, mimetype='image/png')
   except Exception as e:
        return jsonify({"error": str(e)}), 500
   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False) 
   