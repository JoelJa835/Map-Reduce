# Map-Reduce Implementation on Kubernetes for Word Frequency (Project 2024)
*for Principles of Distributed Systems Class, Technical University of Crete*

## Overview

This project implements a Map-Reduce framework on Kubernetes for calculating word frequencies from input files stored in Minio. It involves multiple components such as UI service, authentication service, Cassandra for metadata storage, and Kubernetes-managed workers for executing Map-Reduce tasks.

## Deployment and Cleanup

### Create Kubernetes Deployment

To set up the entire system on Kubernetes:
```bash
make deploy
```

### Clean Kubernetes Deployment

To remove all deployed components from Kubernetes:
```bash
make clean
```

## How to Run

### Using the Client CLI (client.py)

1. **Port Forwarding for UI Service:**

   First, perform port forwarding to access the UI service:
   ```bash
   kubectl port-forward service/ui-service 8080:8080 -n dena
   ```

2. **Admin Operations:**

   - Login as admin:
     ```bash
     python3 client.py login --username admin --password admin
     ```
   
   - Logout:
     ```bash
     python3 client.py logout
     ```

   - Create a new user as admin:
     ```bash
     python3 client.py admin create-user user2
     ```

3. **Job Submission:**

   Submit a job for processing a specific filename (ensure the file is in "map-reduce-input-files" bucket in Minio):
   ```bash
   python3 client.py jobs submit filename
   ```

4. **Job Status:**

   Check the status of a submitted job using its job_id:
   ```bash
   python3 client.py jobs status job_id
   ```

## Additional Scripts in `testing_scripts`

This directory contains scripts useful for development and testing:

1. **display_content.py:** Display contents of a file in Minio.
   
2. **generate_file.py:** Generate input files with a specified number of words and store them in Minio.

3. **test_cassandra.py:** Test connectivity and liveness of Cassandra.

4. **test_minio:** Check the contents of Minio buckets.

## Architecture

### Components

- **UI Service:**
  Flask API handling user commands.

- **Auth Service:**
  API managing user login and token assignment.

- **Cassandra:**
  Distributed data storage for job metadata and temporary data.

- **Manager:**
  Flask API coordinating Map-Reduce execution, managing workers and metadata.

- **Workers:**
  Kubernetes jobs executing Map-Reduce tasks.

- **Minio:**
  Persistent storage for input files, output files, and Map-Reduce chunks.

---


