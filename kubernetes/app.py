from flask import Flask, request, jsonify

app = Flask(__name__)


'''
Api that works as an User interface
'''

# Dummy data for storing job status
job_status = {}

# Dummy data for storing users
users = {}

# Dummy data for storing logged-in users
logged_in_users = set()

# Jobs logic
@app.route('/jobs/submit', methods=['POST'])
def submit_job():
    # Check if user is logged in
    username = request.headers.get('username')
    if not username or username not in logged_in_users:
        return jsonify({"error": "User not logged in"}), 401

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

    if username and password:
        # Placeholder for actual user creation logic
        users[username] = {'password': password}
        return jsonify({"message": f"User '{username}' created successfully"})
    else:
        return jsonify({"error": "Username and password are required"}), 400
    

@app.route('/admin/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    if username in users:
        # Placeholder for actual user deletion logic
        del users[username]
        return jsonify({"message": f"User '{username}' deleted successfully"})
    else:
        return jsonify({"error": f"User '{username}' not found"}), 404


# Login and Logout Logic
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    if username in users and users[username]['password'] == password:
        logged_in_users.add(username)  # Add user to logged-in users
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    username = request.headers.get('username')
    if username and username in logged_in_users:
        logged_in_users.remove(username)  # Remove user from logged-in users
        return jsonify({"message": "Logout successful"})
    else:
        return jsonify({"error": "User not logged in"}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
