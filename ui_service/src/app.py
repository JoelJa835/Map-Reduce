from flask import Flask, request, jsonify
import requests
import os
from typing import Optional
from minio_utils import create_minio_bucket, check_file_existence
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging 
import uuid


app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

# Cassandra connection setup
contact_points = ['cassandra-0.cassandra.dena.svc.cluster.local']
auth_provider = PlainTextAuthProvider(username='admin', password='admin')
keyspace = 'admins'

try:
    cluster = Cluster(contact_points=contact_points, auth_provider=auth_provider)
    session = cluster.connect(keyspace)
except Exception as e:
    logging.error(f"Failed to connect to Cassandra: {e}")
    raise

# Helper functions
def create_jobs_table(session):
    keyspace = session.cluster.metadata.keyspaces.get('admins')
    if keyspace is None:
        raise ValueError("Keyspace does not exist")

    if 'jobs' not in keyspace.tables:
        session.execute("""
            CREATE TABLE jobs (
                job_id UUID PRIMARY KEY,
                input_file TEXT,
                status TEXT
            )
        """)

def submit_job_to_cassandra(session, job_id, input_file):
    insert_query = """
        INSERT INTO jobs (job_id, input_file, status)
        VALUES (%s, %s, %s)
    """
    status = 'submitted'  # Initial status
    try:
        session.execute(insert_query, (job_id, input_file, status))
    except Exception as e:
        logging.error(f"Failed to insert job into Cassandra: {e}")
        raise

# API endpoints
@app.route('/jobs/submit', methods=['POST'])
def submit_job():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    user_info = validate_token(token)
    if not user_info or user_info.get("role") not in ["admin", "user"]:
        return jsonify({"error": "Invalid or expired token or user not authorized"}), 401

    data = request.json
    mapper_func = data.get('mapper_func')
    reducer_func = data.get('reducer_func')
    input_file = data.get('input_file')

    if not input_file:
        return jsonify({"error": "Missing required fields (input_file)"}), 400

    # Check if input file exists in Minio bucket
    if input_file and not check_file_existence(input_file):
        return jsonify({"error": f"File '{input_file}' not found in Minio bucket"}), 404

    # Placeholder for actual job submission logic
    job_id = uuid.uuid4()

    create_jobs_table(session)
    
    # Submit job details to Cassandra
    try:
        submit_job_to_cassandra(session, job_id, input_file)
        return jsonify({"message": "Job submitted successfully", "job_id": str(job_id)}), 200
    except Exception as e:
        logging.error(f"Failed to submit job to Cassandra: {e}")
        return jsonify({"error": f"Failed to submit job to Cassandra: {str(e)}", "job_id": str(job_id), "input_file": input_file}), 500

# Helper to validate token
def validate_token(token: str) -> Optional[dict]:
    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/user-role",
            params={"token": token}
        )
        response.raise_for_status()
        user_role = response.json()  # Assuming the response is a JSON string with the role
        return {"role": user_role}
    except requests.RequestException as e:
        print(f"Token validation failed: {e}")
        return None


# Retrieve job status from Cassandra
def get_job_status_from_cassandra(job_id):
    select_query = """
        SELECT * FROM jobs WHERE job_id = %s
    """
    try:
        result = session.execute(select_query, (job_id,))
        row = result.one()  # Assuming job_id is unique; use result if multiple rows expected
        if row:
            return {"job_id": str(row.job_id), "status": row.status}
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to fetch job status from Cassandra: {e}")
        raise


@app.route('/jobs/status/<uuid:job_id>', methods=['GET'])
def get_job_status(job_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    user_info = validate_token(token)
    if not user_info or user_info.get("role") not in ["admin", "user"]:
        return jsonify({"error": "Invalid or expired token or user not authorized"}), 401

    try:
        job_status = get_job_status_from_cassandra(job_id)
        if job_status:
            return jsonify(job_status)
        else:
            return jsonify({"error": "Job not found"}), 404
    except Exception as e:
        logging.error(f"Failed to get job status: {e}")
        return jsonify({"error": f"Failed to get job status: {str(e)}"}), 500
    


# Admin Logic
@app.route('/admin/create_user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    email = data.get('email', '')

    if username and password and email:
        # Prepare the payload for the FastAPI request
        payload = {
            "username": username,
            "password": password,
            "email": email
        }

        # Send a request to the FastAPI auth service
        headers = {
            'Authorization': f'Bearer {request.headers.get("Authorization")}'  # Forward the token
        }
        response = requests.post(AUTH_SERVICE_URL + "/signup", json=payload, headers=headers)

        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify(response.json()), response.status_code
    else:
        return jsonify({"error": "Username, password, and email are required"}), 400

# @app.route('/admin/delete_user/<username>', methods=['DELETE'])
# def delete_user(username):
#     if username in users:
#         # Placeholder for actual user deletion logic
#         del users[username]
#         return jsonify({"message": f"User '{username}' deleted successfully"})
#     else:
#         return jsonify({"error": f"User '{username}' not found"}), 404



# Logic Logic
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    print(AUTH_SERVICE_URL)
    # Send a request to the auth service
    response = requests.post(AUTH_SERVICE_URL + "/token", data={'username': username, 'password': password})
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    


# Helpher to check minio is running
MINIO_ENDPOINT = "http://minio-service:9000"

# Example endpoint to test MinIO connection
@app.route('/minio/health/live', methods=['GET'])
def check_minio_health():
    try:
        response = requests.get(f"{MINIO_ENDPOINT}/minio/health/live")
        response.raise_for_status()
        return jsonify({"status": "MinIO is healthy"})
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to connect to MinIO: {e}"}), 500

# Entry point
if __name__ == '__main__':
    create_minio_bucket()
    app.run(host='0.0.0.0', port=8080, debug=True)
