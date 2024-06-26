from flask import Flask, request, jsonify
import logging
import uuid
from utils import validate_token
from minio_utils import create_minio_bucket, check_file_existence
from db_utils import submit_job_to_cassandra, get_job_status_from_cassandra, create_jobs_table
import requests
import os

app = Flask(__name__)

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")
MINIO_ENDPOINT = os.getenv("MINIO_SERVICE_URL", "minio-service:9000")
MANAGER_SERVICE_URL = os.getenv("MANAGER_SERVICE_URL", "http://manager-service.dena:8081")



@app.route('/jobs/submit', methods=['POST'])
def submit_job():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    user_info = validate_token(token)
    if not user_info or user_info.get("role") not in ["admin", "user"]:
        return jsonify({"error": "Invalid or expired token or user not authorized"}), 401

    data = request.json
    input_file = data.get('input_file')

    if not input_file:
        return jsonify({"error": "Missing required fields (input_file)"}), 400

    if input_file and not check_file_existence(input_file):
        return jsonify({"error": f"File '{input_file}' not found in Minio bucket"}), 404

    job_id = uuid.uuid4()
    create_jobs_table()

    try:
        submit_job_to_cassandra(job_id, input_file)

        # Send request to the manager service
        payload = {
            'job_id': str(job_id),
            'input_file': input_file
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token  # Forward the token if needed by the manager service
        }
        response = requests.post(f'{MANAGER_SERVICE_URL}/initialize_job', json=payload, headers=headers)

        if response.status_code == 200:
            return jsonify({"message": "Job submitted successfully and forwarded to manager service", "job_id": str(job_id)}), 200
        else:
            logging.error(f"Failed to forward job to manager service: {response.status_code}, {response.text}")
            return jsonify({"error": f"Failed to forward job to manager service: {response.text}"}), response.status_code

    except Exception as e:
        logging.error(f"Failed to submit job to Cassandra: {e}")
        return jsonify({"error": f"Failed to submit job to Cassandra: {str(e)}", "job_id": str(job_id), "input_file": input_file}), 500


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



@app.route('/admin/create_user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    email = data.get('email', '')

    if username and password and email:
        payload = {"username": username, "password": password, "email": email}
        headers = {'Authorization': f'Bearer {request.headers.get("Authorization")}'}
        response = requests.post(AUTH_SERVICE_URL + "/signup", json=payload, headers=headers)

        if response.status_code == 201:
            return jsonify(response.json())
        else:
            return jsonify(response.json()), response.status_code
    else:
        return jsonify({"error": "Username, password, and email are required"}), 400



@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    response = requests.post(AUTH_SERVICE_URL + "/token", data={'username': username, 'password': password})
    
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Invalid username or password"}), 401


@app.route('/minio/health/live', methods=['GET'])
def check_minio_health():
    try:
        response = requests.get(f"{MINIO_ENDPOINT}/minio/health/live")
        response.raise_for_status()
        return jsonify({"status": "MinIO is healthy"})
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to connect to MinIO: {e}"}), 500

if __name__ == '__main__':
    create_minio_bucket()
    app.run(host='0.0.0.0', port=8080, debug=True)
