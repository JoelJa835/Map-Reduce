from flask import Flask, request, jsonify
import logging
from utils import initiate_split_job
from db_utils import update_job_status


NUM_CHUNKS = 10

app = Flask(__name__)



@app.route('/initialize_job', methods=['POST'])
def initialize_job():
    data = request.json
    job_id = data.get('job_id')
    filename = data.get('input_file')
    

    if not job_id or not filename:
        return jsonify({"error": "Missing required fields (job_id, filename)"}), 400

    try:
        update_job_status(job_id, 'splitting_start')
        initiate_split_job(job_id, filename, NUM_CHUNKS)
        # Call the kubernetes job to split

        return jsonify({"message": "Job splitting started", "job_id": job_id}), 200

    except Exception as e:
        logging.error(f"Failed to initialize job: {e}")
        return jsonify({"error": f"Failed to initialize job: {str(e)}"}), 500



@app.route('/split_complete', methods=['POST'])
def split_complete():
    data = request.json
    job_id = data.get('job_id')
    prefix = data.get('prefix')
    num_chunks = data.get('num_chunks')

    try:
        # Verify chunks exist in Minio
        # Implement Minio verification logic here

        update_job_status(job_id, 'splitting_complete')
        # Optionally update the job table with num_chunks and prefix
        return jsonify({"message": "Job splitting complete", "job_id": job_id}), 200

    except Exception as e:
        logging.error(f"Failed to complete splitting job: {e}")
        return jsonify({"error": f"Failed to complete splitting job: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)



