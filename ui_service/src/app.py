from flask import Flask, request, jsonify

app = Flask(__name__)


'''
Api that works as an User interface
'''

# Dummy data for storing job status
job_status = {}

# Dummy data for storing users
users = {}

# Jobs logic
@app.route('/jobs/submit', methods=['POST'])
def submit_job():
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



# Logic Logic
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')

    if username in users and users[username]['password'] == password:
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
