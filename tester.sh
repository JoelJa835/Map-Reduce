# first run minikube tunnel in another terminal

chmod +x tester.sh

curl -X GET http://localhost:8080/jobs/status/2  



# run the auth service in docker
docker run -d --name map-reduce-auth-service -p 8000:8000 map-reduce-auth-service
# with logs
docker run -t --name map-reduce-auth -p 8000:8000 map-reduce-auth



# sing a user in:
gsiatras@192 Map-Reduce % curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJleHAiOjE3MTgxMjUyOTZ9.A52H8Mor2LvBujm93wFPZ-Ty8WGPky3BLMz8RYlyysg' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user1", 
  "email": "user1@gmail.com",
  "role": "user",
  "password": "password"
}'


# log in
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=user1&password=password&scope=&client_id=string&client_secret=string'
