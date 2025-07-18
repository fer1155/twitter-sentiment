# twitter-sentiment
A project to the 'infraestructuras paralelas y distribuidas 'class, using flask, ray and docker-compose

To run download the repository, then in the root of the project (console) write this:
  
  docker-compose build
  docker-compose up

Endpoints to execute (all whit the method get):

http://localhost:5001/sentiment-data
http://localhost:5002/proccess-data
http://localhost:5003/download-market-data
http://localhost:5004/build-portfolio
http://localhost:5005/plot

