# twitter-sentiment
A project to the 'infraestructuras paralelas y distribuidas 'class, using flask, ray and docker-compose

To run download the repository, then in the root of the project (console) write this:
  
  1) docker-compose build
  2) docker-compose up

Endpoints to execute (all whit the method get):

  1) http://localhost:5001/sentiment-data
  2) http://localhost:5002/proccess-data
  3) http://localhost:5003/download-market-data
  4) http://localhost:5004/build-portfolio
  5) http://localhost:5005/plot
