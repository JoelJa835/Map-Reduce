# Map-Reduce
Implementation of Map-Reduce on Kubernetes for word frequency (Project 2024) for Principles of Distributed Systems Class / Technical University of Crete.     


**Create the k8s deployment**                
make deploy: sets up everything in kubernetes            
    
**Clean the k8s deployment**         
make clean: clean everything in kubernetes        

**How to run**            
client.py is our cli:
1. first run a portforward on kubernetes for the ui-service:        
kubectl port-forward service/ui-service 8080:8080 -n dena        
2. Admin Login:
python3 client.py login --username admin --password admin
3. Logout:
python3 client.py logout
4. Admin create user:
python3 client.py admin create-user user2
5. Job submit:
python3 client.py jobs submit filename (filename must be already inserted in the "map-reduce-input-files" bucket in minio"
6. Job status:
python3 client.py jobs status job_id


**testing_scripts:**        
Contains some scipts/files helpful for the developement/testing
1. display_content.py:
Displays the contents of a file in minio
2. generate_file.py:
Generates input files with a given number of words and stores them in minio
3. test_cassandra.py:
Test cassandara liveness
4. test_minio:
Check the contents of minio buckets


***Architecture***
