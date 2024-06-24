# first run minikube tunnel in another terminal

chmod +x tester.sh

curl -X GET http://localhost:8080/jobs/status/2  



# run the auth service in docker
docker run -d --name map-reduce-auth-service -p 8000:8000 map-reduce-auth-service
# with logs
docker run -t --name map-reduce-auth -p 8000:8000 map-reduce-auth


# Auth
# sing a user in:
curl -X 'POST' \
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



# UI
# submit a job
curl -X POST http://localhost:8080/jobs/submit \
-H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJleHAiOjE3MTgyMDc2MDF9.kfmhhD6iaABBYeHDYQIV-xORjvgUHUEvS_-vyiGFFSk" \
-H "Content-Type: application/json" \
-d '{
  "mapper_func": "function mapper(key, value) { return key + value; }",
  "reducer_func": "function reducer(key, values) { return values.reduce((a, b) => a + b, 0); }",
  "input_data": {"key1": "value1", "key2": "value2"}
}'


# Get job status
curl -X GET http://10.5.0.3:8080/jobs/status/1 \
-H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJleHAiOjE3MTgyMDc2MDF9.kfmhhD6iaABBYeHDYQIV-xORjvgUHUEvS_-vyiGFFSk"


# login
curl -X POST http://localhost:8080/login \
-H "Content-Type: application/json" \
-d '{"username": "admin", "password": "admin"}'   


# Sign in a user
curl -X POST http://localhost:8080/admin/create_user \
-H "Content-Type: application/json" \
-H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlkIjoxLCJleHAiOjE3MTgyMDg1OTl9.-_ieELVCUHJvWdwOs0I4DqjKDNTnXN8SqFQepgPifB0" \
-d '{"username": "user1", "password": "password123", "email": "user1@example.com"}'



# CLIENT
kubectl port-forward service/ui-service 8080:8080 -n dena
# login 
python3 client.py login --username admin --password admin

# add a user
python3 client.py admin create-user user2


kubectl create -f minio-storage-class.yaml
kubectl create -f minio-pv.yaml
kubectl create -f minio-pvc.yaml
kubectl create -f minio-deployment.yaml

kubectl delete -f minio-deployment.yaml
kubectl delete -f minio-pvc.yaml
kubectl delete -f minio-pv.yaml
kubectl delete -f minio-storage-class.yaml



#fix for kubernetes storages
kubectl patch pv cassandra-data-pv-1 -p '{"metadata":{"finalizers":null}}'

kubectl rollout restart deployment ui-deployment -n dena

kubectl rollout restart statefulset manager-service -n dena

kubectl exec -it cassandra-0 -n dena -- /bin/bash

cqlsh

kubectl delete pods --field-selector=status.phase==Succeeded -n dena
