import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick 
import datetime as dt
import yfinance as yf
import os
import ray
from flask import Flask, jsonify

matplotlib.use('Agg') # nuevo (# Para poder graficar sin interfaz)
plt.style.use('ggplot')

#data_folder = 'C:/Users/Fer/Desktop/Proyecto2-TwitterSentiment'
data_folder = os.getcwd()

ray.init(ignore_reinit_error=True) # Inicia Ray (usa todos los núcleos disponibles)

app = Flask(__name__)

#----------------------------------------------------------------------
#Primer microservicio
#----------------------------------------------------------------------
#Create dataframe 'sentiment_df' from .cvs file
@ray.remote
def makeSentimentDf():
    sentiment_df = pd.read_csv(os.path.join(data_folder, 'sentiment_data.csv'))
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df = sentiment_df[~sentiment_df['symbol'].isin(['ATVI', 'MRO'])]
    sentiment_df = sentiment_df.set_index(['date', 'symbol'])
    sentiment_df['engagement_ratio'] = sentiment_df['twitterComments']/sentiment_df['twitterLikes']
    sentiment_df = sentiment_df[(sentiment_df['twitterLikes']>20)&(sentiment_df['twitterComments']>10)]
    return sentiment_df
#----------------------------------------------------------------------
#Segundo microservicio
#----------------------------------------------------------------------
#Create dataframe 'aggragated_df' from sentiment_df, with two columns (mensual engagement ratio, ranking)
def makeAggragatedDf(sentiment_df):
   aggragated_df = (sentiment_df.reset_index('symbol').groupby([pd.Grouper(freq='ME'), 'symbol']) [['engagement_ratio']].mean())
   aggragated_df['rank'] = (aggragated_df.groupby(level=0)['engagement_ratio'].transform(lambda x: x.rank(ascending=False)))
   return aggragated_df

#Apply filter to the dataframe 'aggragated_df', for take the 5 best ranked symbols per month
def applyFilter(aggragated_df):
   filtered_df = aggragated_df[aggragated_df['rank']<6].copy()
   filtered_df = filtered_df.reset_index(level=1)
   filtered_df.index = filtered_df.index+pd.DateOffset(1)
   filtered_df = filtered_df.reset_index().set_index(['date', 'symbol'])
   #filtered_df.head(20)
   return filtered_df

#Create a dictionary where the key is a unique date and the value is a list of stock symbols
def makeDictionary(filtered_df):
   dates = filtered_df.index.get_level_values('date').unique().tolist()
   fixed_dates = {}
   for d in dates:
    fixed_dates[d.strftime('%Y-%m-%d')] = filtered_df.xs(d, level=0).index.tolist()
   return fixed_dates
#----------------------------------------------------------------------
#tercer microservicio
#----------------------------------------------------------------------
#Download historical prices of all stocks (acciones) using yfinance
@ray.remote
def downloadHistoricalPrices(sentiment_df):
   stocks_list = sentiment_df.index.get_level_values('symbol').unique().tolist()
   prices_df = yf.download(tickers=stocks_list, start='2021-01-01', end='2023-03-01')
   return prices_df
#----------------------------------------------------------------------
#Cuarto microservicio
#----------------------------------------------------------------------
#Build a monthly portfolio with the stocks with the best engagement on Twitter
@ray.remote  
def buildMonthlyPortfolio(prices_df, fixed_dates):
   returns_df = np.log(prices_df['Close']).diff().dropna()
   portfolio_df = pd.DataFrame()
   for start_date in fixed_dates.keys():
      end_date = (pd.to_datetime(start_date)+pd.offsets.MonthEnd()).strftime('%Y-%m-%d')
      cols = fixed_dates[start_date]
      temp_df = returns_df[start_date:end_date][cols].mean(axis=1).to_frame('portfolio_return')
      portfolio_df = pd.concat([portfolio_df, temp_df], axis=0)
   return portfolio_df

#Update the portfolio with a new column 'nasdaq_return', previusly download
@ray.remote
def updatePortfolio(portfolio_df):
   qqq_df = yf.download(tickers='QQQ', start='2021-01-01', end='2023-03-01')
   qqq_ret = np.log(qqq_df['Close']).diff()
   qqq_ret.columns = ['nasdaq_return']  
   portfolio_df = portfolio_df.merge(qqq_ret, left_index=True, right_index=True)
   return portfolio_df
#----------------------------------------------------------------------
#Plot (graficar) the two columns of the portfolio in a graph
@ray.remote
def plotPortfolio(portfolio_dff):
   portfolios_cumulative_return = np.exp(np.log1p(portfolio_dff).cumsum()).sub(1)
   portfolios_cumulative_return.plot(figsize=(16,6))
   plt.title('Twitter Engagement Ratio Strategy Return Over Time')
   plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1))
   plt.ylabel('Return')
   #plt.show()
   plt.savefig("retorno_estrategia.png")
   return "retorno_estrategia.png"

@app.route("/generar", methods=["GET"])
def generar():
    sentimentDf_ref = makeSentimentDf.remote()
    sentimentDf = ray.get(sentimentDf_ref)
    aggragatedDf = makeAggragatedDf(sentimentDf)
    filteredDf = applyFilter(aggragatedDf)
    fixedDates = makeDictionary(filteredDf)
    pricesDf_ref = downloadHistoricalPrices.remote(sentimentDf)
    pricesDf = ray.get(pricesDf_ref)
    portfolioDf_ref = buildMonthlyPortfolio.remote(pricesDf, fixedDates)
    portfolioDf = ray.get(portfolioDf_ref)
    updatedDf_ref = updatePortfolio.remote(portfolioDf)
    updatedDf = ray.get(updatedDf_ref)
    image_path_ref = plotPortfolio.remote(updatedDf)
    image_path = ray.get(image_path_ref)
    print("Se llegó al final del endpoint /generar")
    return jsonify({"message": "Análisis completado", "Image": image_path})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

#if __name__ == "__main__":
#   sentimentDf = makeSentimentDf()
#   aggragatedDf = makeAggragatedDf(sentimentDf)
#   filteredDf = applyFilter(aggragatedDf)
#   fixedDates = makeDictionary(filteredDf)
#   pricesDf = downloadHistoricalPrices(sentimentDf)
#   portfolioDf = buildMonthlyPortfolio(pricesDf, fixedDates)
#   portfolioDfAct = updatePortfolio(portfolioDf)
#   plotPortfolio(portfolioDfAct)