# Map-Reduce Implementation on Kubernetes (Project 2024)
*for Principles of Distributed Systems Class, Technical University of Crete*

## Overview

This project implements a Map-Reduce framework on Kubernetes to compute word frequencies from input files stored in Minio. It utilizes various components such as UI service, authentication service, Cassandra for metadata storage, and Kubernetes-managed workers for executing Map-Reduce tasks.

## Deployment and Cleanup

### Create Kubernetes Deployment

To deploy the entire system on Kubernetes:
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

   Forward the UI service port to access it locally:
   ```bash
   kubectl port-forward service/ui-service 8080:8080 -n dena
   ```

2. **Admin Operations:**

   - **Login as admin:**
     ```bash
     python3 client.py login --username admin --password admin
     ```
   
   - **Logout:**
     ```bash
     python3 client.py logout
     ```

   - **Create a new user as admin:**
     ```bash
     python3 client.py admin create-user user2
     ```

3. **Job Submission:**

   Submit a job to process a specific filename (ensure the file is in "map-reduce-input-files" bucket in Minio):
   ```bash
   python3 client.py jobs submit filename
   ```

4. **Job Status:**

   Check the status of a submitted job using its job_id:
   ```bash
   python3 client.py jobs status job_id
   ```

## Additional Scripts in `testing_scripts`

This directory includes useful scripts for development and testing:

1. **display_content.py:** Displays contents of a file stored in Minio.
   
2. **generate_file.py:** Generates input files with a specified number of words and stores them in Minio.

3. **test_cassandra.py:** Tests connectivity and functionality of Cassandra.

4. **test_minio:** Checks the contents of Minio buckets.

## Architecture

### Components

- **UI Service:**
  Flask API handling user commands.

- **Auth Service:**
  FastAPI managing user login and token assignment.

- **Cassandra:**
  Distributed data storage for job metadata and temporary data.

- **Manager:**
  Flask API coordinating Map-Reduce execution, managing workers, and metadata.

- **Workers:**
  Kubernetes jobs executing Map-Reduce tasks.

- **Minio:**
  Persistent storage for input files, output files, and Map-Reduce chunks.

## Map-Reduce Algorithm Workflow

1. **Job Initialization:**
   - UI service forwards a job to `/initialize_job` endpoint of Manager service, storing job metadata in Cassandra with status initialized.

2. **Split Phase (Worker Job - Split):**
   - Worker job retrieves the input file from Minio, splits it into chunks, and stores them in a Minio bucket (`chunk_bucket`). It notifies the Manager service upon completion.

3. **Map Phase (Worker Job - Map):**
   - Manager creates mapper jobs based on the number of chunks.
   - Mapper jobs retrieve chunks from Minio, perform mapping, and store data in Cassandra (`map_table`). They notify the Manager upon completion.

4. **Shuffle-Sort Phase (Worker Job - Shuffle-Sort):**
   - Manager aggregates and sorts mapped data into `shuffle_sort_table` in Cassandra.
   - Worker job retrieves data, performs shuffling and sorting, and stores results back in Cassandra. It notifies the Manager upon completion.

5. **Reduce Phase (Worker Job - Reduce):**
   - Manager creates reducer jobs based on configured reducers.
   - Reducer jobs retrieve data from Cassandra, perform reduction operations, and store results in `reduce_table`. They notify the Manager upon completion.

6. **Combine Phase (Worker Job - Combine):**
   - Manager initiates a combine job to aggregate reduced results.
   - Worker job retrieves data from Cassandra, performs combining, and stores the output JSON file in the output Minio bucket. It notifies the Manager upon completion.

7. **Job Completion:**
   - Manager updates job status to completed upon receiving notification from the combine job.






