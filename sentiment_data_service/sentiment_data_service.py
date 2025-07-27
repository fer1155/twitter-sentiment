import pandas as pd
from flask import Flask, jsonify, Response
import os

app = Flask(__name__)

#data_folder = 'C:/Users/Fer/Desktop/Proyecto2-TwitterSentiment'

#Access the current docker directory to save the data folder 
data_folder = os.path.join(os.getcwd(), "data")

#Create dataframe 'sentiment_df' from .cvs file
def makeSentimentDf():
    sentiment_df = pd.read_csv(os.path.join(data_folder, 'sentiment_data.csv'))
    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    sentiment_df = sentiment_df[~sentiment_df['symbol'].isin(['ATVI', 'MRO'])]
    sentiment_df = sentiment_df.set_index(['date', 'symbol'])
    sentiment_df['engagement_ratio'] = sentiment_df['twitterComments']/sentiment_df['twitterLikes']
    sentiment_df = sentiment_df[(sentiment_df['twitterLikes']>20)&(sentiment_df['twitterComments']>10)]
    return sentiment_df

#Define the endpoint to make the sentiment dataframe
@app.route("/sentiment-data", methods=["GET"])
def get_sentiment_data():
    try:
        sentimentDF = makeSentimentDf()
        return Response(sentimentDF.reset_index().to_json(orient="records"), mimetype='application/json')
    except Exception as e:
        return jsonify({"Error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)