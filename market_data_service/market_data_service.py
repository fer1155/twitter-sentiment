import pandas as pd
import yfinance as yf
import ray
from flask import Flask, jsonify
import requests

ray.init(ignore_reinit_error=True) # Inicia Ray (usa todos los núcleos disponibles)
app = Flask(__name__)

#Get data of 'sentiment_data_service' microservice  
def get_sentiment_df(): 
   datosEnJson = requests.get("http://sentiment:5000/sentiment-data")
   sentiment_df = pd.read_json(datosEnJson.text)
   sentiment_df['date'] = pd.to_datetime(sentiment_df['date']) 
   return sentiment_df

#Download historical prices of all stocks (acciones) using yfinance
@ray.remote
def downloadHistoricalPrices(symbol):
   prices_df = yf.download(tickers=symbol, start='2021-01-01', end='2023-03-01')
   
   # Manejar MultiIndex columns (cuando se descarga un solo símbolo)
   if isinstance(prices_df.columns, pd.MultiIndex):
    prices_df.columns = prices_df.columns.droplevel(1)
   
   # Reset index para obtener Date como columna
   prices_df = prices_df.reset_index()
   
   # Crear el DataFrame resultado
   result_df = pd.DataFrame()
   result_df['date'] = prices_df['Date'].dt.strftime('%Y-%m-%d')
   result_df['ticker'] = symbol
   
   # Si Close es una Serie, usar .values para obtener array 1D
   close_values = prices_df['Close'].values
   
   # Si es 2D, aplanar
   if len(close_values.shape) > 1:
    close_values = close_values.flatten()
   
   result_df['close'] = pd.Series(close_values).round(2)
   
   return result_df

#Define the endpoint to download the market data with ray (to make the process parallel) and filter it, then 
#return a dataframe with the processed data.
@app.route("/download-market-data", methods=["GET"])
def get_market_data():
   try:
      sentiment_data = get_sentiment_df()
      stocks_list = sentiment_data['symbol'].unique().tolist()
      
      #Descargar datos en paralelo
      futuros = []
      for symbol in stocks_list:
         futuros.append(downloadHistoricalPrices.remote(symbol))
      datos_descargados = ray.get(futuros)

      #Filtrar y concatenar datos válidos
      datos_validos = [df for df in datos_descargados if not df.empty]
      
      #Combinar todos los datos
      pricesDf = pd.concat(datos_validos, ignore_index=True)

      # Ordenar por ticker y fecha
      pricesDf = pricesDf.sort_values(['ticker', 'date'])
      
      return jsonify({"data": pricesDf.to_dict('records'),})
   except Exception as e:
      return jsonify({"error": str(e)}), 500
   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)