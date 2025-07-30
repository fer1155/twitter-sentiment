import time
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

#Define the endpoint to process the sentiment data with ray (to make the process parallel) and filter it, then 
#create a dictionary with the answer.
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

@app.route("/metrica", methods=["GET"])
def get_metrica():
   try:
      # Medir tiempo de procesamiento paralelo
      start_time_parallel = time.time()
      result_parallel = requests.get("http://process:5000/proccess-data")
      end_time_parallel = time.time()
      parallel_time = end_time_parallel - start_time_parallel

      # Medir tiempo de procesamiento secuencial
      start_time_sequential = time.time()
      sentiment_data = get_sentiment_df()
      result_sequential = ejecuion_secuencial(sentiment_data)
      end_time_sequential = time.time()
      sequential_time = end_time_sequential - start_time_sequential

      return jsonify({
         "performance_comparison": {
               "parallel_processing": {
                  "time_seconds": round(parallel_time, 4),
                  "method": "Ray parallel processing"
               },
               "sequential_processing": {
                  "time_seconds": round(sequential_time, 4),
                  "method": "Sequential processing"
               }
         }
      })
   except Exception as e:
      return jsonify({"error": f"Processing error: {str(e)}"}), 500

def ejecuion_secuencial(sentiment_df):
   try:
      aggragated_df = (sentiment_df.reset_index('symbol').groupby([pd.Grouper(freq='ME'), 'symbol'])
                    [['engagement_ratio']].mean())
      aggragated_df['rank'] = (aggragated_df.groupby(level=0)['engagement_ratio']
                         .transform(lambda x: x.rank(ascending=False)))
      filtered_df = aggragated_df[aggragated_df['rank']<6].copy()
      filtered_df = filtered_df.reset_index(level=1)
      filtered_df.index = filtered_df.index+pd.DateOffset(1)
      filtered_df = filtered_df.reset_index().set_index(['date', 'symbol'])
      dates = filtered_df.index.get_level_values('date').unique().tolist()
      fixed_dates = {}
      for d in dates:
         fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
      return fixed_dates
   except Exception as e:
      return jsonify({"error": f"Processing error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)