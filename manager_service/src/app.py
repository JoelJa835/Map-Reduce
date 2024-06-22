from flask import Flask, request, jsonify
import os
from db_utils import update_job_status
import logging



app = Flask(__name__)


@app.route('/initialize_job', methods=['POST'])
def initialize_job():
    data = request.json
    job_id = data.get('job_id')

    if not job_id:
        return jsonify({"error": "Missing required field (job_id)"}), 400

    try:
        update_job_status(job_id, 'initialized')
        return jsonify({"message": "Job initialized successfully", "job_id": job_id}), 200
    except Exception as e:
        logging.error(f"Failed to initialize job: {e}")
        return jsonify({"error": f"Failed to initialize job: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
