# initial admin
curl -X 'POST' \
  'http://localhost:8000/initial-admin' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "admin",
  "email": "admin@gmail.com",
  "role": "admin",
  "password": "admin"
}'

#sign up
curl -X 'POST' \
  'http://localhost:8000/signup' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJleHAiOjE3MTgwMzU1ODh9.XkUP2GsbM_zGB3HhHtyLMCbgNZihNmmby1XBpCGFsP4' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "user1",
  "email": "asdsad",
  "role": "user",
  "password": "password"
}'

#signin
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=string&password=string&scope=&client_id=string&client_secret=string'