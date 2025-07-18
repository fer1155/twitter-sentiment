import pandas as pd
import ray
from flask import Flask, jsonify
import requests
#import logging

app = Flask(__name__)
ray.init(ignore_reinit_error=True) # Inicia Ray (usa todos los núcleos disponibles)
#logging.basicConfig(level=logging.INFO)

#Get data of 'sentiment_data_service' microservice  
def get_sentiment_df(): 
   datosEnJson = requests.get("http://sentiment:5000/sentiment-data")
   sentiment_df = pd.read_json(datosEnJson.text)
   sentiment_df['date'] = pd.to_datetime(sentiment_df['date']) 
   return sentiment_df

#Calculate the en mensualy engagement and ranking, for each month
@ray.remote
def process_month(month, month_df):
    monthly_average = month_df.groupby('symbol')[['engagement_ratio']].mean()
    monthly_average['rank'] = monthly_average['engagement_ratio'].rank(ascending=False)
    monthly_average['date'] = month
    return monthly_average[monthly_average['rank'] < 6]

#Create a dictionary where the key is a unique date and the value is a list of stock symbols
def makeDictionary(filtered_df):
   dates = filtered_df.index.get_level_values('date').unique()
   fixed_dates = {}
   for d in dates:
    symbols = filtered_df.loc[d].index.tolist()
    fixed_dates[d.strftime('%Y-%m-%d')] = symbols
   return fixed_dates

@app.route("/proccess-data", methods=["GET"])
def make_fixed_dates():
   try:
      sentiment_data = get_sentiment_df()

      #Agrupar datos por mes
      meses_dt = sentiment_data.groupby(pd.Grouper(key='date', freq='ME'))
      
      futuros = []
      for columna, fila in meses_dt:
         futuros.append(process_month.remote(columna, fila))
      mejores_meses = ray.get(futuros)

      #dataframe whit the 5 highest ranked symbols per month
      filtered_df = pd.concat(mejores_meses)

      #Ajustar indices
      filtered_df = filtered_df.reset_index()
      filtered_df['date'] = filtered_df['date'] + pd.DateOffset(1)
      filtered_df.set_index(['date', 'symbol'], inplace=True)
      
      fixedDates = makeDictionary(filtered_df)
      return jsonify(fixedDates)
   
   except Exception as e:
        return jsonify({"error": str(e)}), 500
   
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)