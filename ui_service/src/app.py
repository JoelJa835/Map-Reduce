from flask import Flask, request, jsonify
import requests
import os
from typing import Optional


app = Flask(__name__)


'''
Api that works as an User interface
'''


AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000")

# Dummy data for storing job status
job_status = {}

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


# Jobs logic
@app.route('/jobs/submit', methods=['POST'])
def submit_job():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    user_info = validate_token(token)
    if not user_info or user_info.get("role") not in ["admin", "user"]:
        return jsonify({"error": "Invalid or expired token or user not authorized"}), 401

    data = request.json
    mapper_func = data.get('mapper_func', '')
    reducer_func = data.get('reducer_func', '')
    input_data = data.get('input_data', {})

    # Placeholder for actual job submission logic
    job_id = len(job_status) + 1
    job_status[job_id] = 'submitted'

    return jsonify({"message": "Job submitted successfully", "job_id": job_id})



@app.route('/jobs/status/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "Authorization token is missing"}), 401

    user_info = validate_token(token)
    if not user_info or user_info.get("role") not in ["admin", "user"]:
        return jsonify({"error": "Invalid or expired token or user not authorized"}), 401

    if job_id in job_status:
        return jsonify({"job_id": job_id, "status": job_status[job_id]})
    else:
        return jsonify({"error": "Job not found"}), 404
    


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
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)