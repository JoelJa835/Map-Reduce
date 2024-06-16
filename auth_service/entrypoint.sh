#!/bin/sh

# Start the FastAPI application in the background
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Wait for the FastAPI application to start
sleep 5

# Send a POST request to create the initial admin user
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

# Keep the container running
tail -f /dev/null
