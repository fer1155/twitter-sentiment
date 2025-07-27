import pandas as pd
import numpy as np
import yfinance as yf
import ray
from flask import Flask, jsonify, Response
import requests

ray.init(ignore_reinit_error=True) # Inicia Ray (usa todos los núcleos disponibles)
app = Flask(__name__)

#Get data of 'process data' microservice  
def get_fixed_dates(): 
   datosEnJson = requests.get("http://process:5000/proccess-data")
   fixed_dates = datosEnJson.json()
   return fixed_dates

#Get data of 'market data' microservice  
def get_prices_df(): 
   datosEnJson = requests.get("http://marketdata:5000/download-market-data")
   prices_df = pd.read_json(datosEnJson.text)
 
   # Expandir la columna 'data' si es una lista o una serie de dicts
   if 'data' in prices_df.columns:
       df = pd.json_normalize(prices_df['data'])  # convierte los dicts en columnas
   else:
       raise ValueError("La columna 'data' no está en el DataFrame recibido.")
   
   df = df.pivot(index='date', columns='ticker', values='close')
   df.columns = pd.MultiIndex.from_product([['close'], df.columns])
   #print(df.head)
   #print(df.columns)
   return df

#Build a monthly portfolio with the stocks with the best engagement on Twitter
def buildMonthlyPortfolio(prices_df, fixed_dates):
   returns_df = np.log(prices_df['close']).diff().dropna()
   portfolio_df = pd.DataFrame()
   for start_date in fixed_dates.keys():
      end_date = (pd.to_datetime(start_date)+pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
      cols = fixed_dates[start_date]
      temp_df = returns_df[start_date:end_date][cols].mean(axis=1).to_frame('portfolio_return')
      portfolio_df = pd.concat([portfolio_df, temp_df], axis=0)
   return portfolio_df

#Update the portfolio with a new column 'nasdaq_return', previusly download
def updatePortfolio(portfolio_df):
   qqq_df = yf.download(tickers='QQQ', start='2021-01-01', end='2023-03-01')
   qqq_ret = np.log(qqq_df['Close']).diff()
   qqq_ret.columns = ['nasdaq_return']  
   portfolio_df.index = pd.to_datetime(portfolio_df.index)
   qqq_ret.index = pd.to_datetime(qqq_ret.index)
   portfolio_df = portfolio_df.merge(qqq_ret, left_index=True, right_index=True, how='inner')
   portfolio_df = portfolio_df.dropna() 
   return portfolio_df

#Define the endpoint to build a portfolio as dataframe
@app.route("/build-portfolio", methods=["GET"])
def build_portfolio_service():
   try:
      fixed_dates = get_fixed_dates()
      prices_df = get_prices_df()
      portfolioDf = buildMonthlyPortfolio(prices_df, fixed_dates)
      portfolio_df_update = updatePortfolio(portfolioDf)
      return Response(portfolio_df_update.to_json(), mimetype='application/json')
   except Exception as e:
        return jsonify({"error": str(e)}), 500
   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)