from flask import Flask, request, jsonify
import logging
from utils import initiate_split_job, initialize_map_phase, initialize_shuffle_sort_phase
from db_utils import update_job_status, update_job_chunks, get_job_status_and_chunk, update_job_sub_status, empty_entries
from minio_utils import delete_chunk


app = Flask(__name__)

NUM_CHUNKS = 10
REDUCERS = 4


MAP_TABLE = 'map_table'
SHUFFLE_TABLE = 'shuffle_table'
REDUCE_TABLE = 'reduce_table'

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
        update_job_status(job_id, 'mapping_start')
        update_job_chunks(job_id, num_chunks)
        # Optionally update the job table with num_chunks and prefix

        # Initialize the map phase
        initialize_map_phase(job_id)
        return jsonify({"message": "Job splitting complete", "job_id": job_id}), 200

    except Exception as e:
        logging.error(f"Failed to complete splitting job: {e}")
        return jsonify({"error": f"Failed to complete splitting job: {str(e)}"}), 500



@app.route('/map_complete', methods=['POST'])
def map_complete():
    data = request.json
    job_id = data.get('job_id')
    prefix = data.get('prefix')
    chunk_name = data.get('chunk_name')

    try:
        # Delete chunk from bucket
        delete_chunk(chunk_name)

        # Get job substatus and number of chunks
        sub_status, num_chunks = get_job_status_and_chunk(job_id)

        if sub_status is None:
            sub_status = 0
            
        sub_status = sub_status + 1
        if sub_status == num_chunks:
            # Initialize shuffle_sort phase
            update_job_status(job_id, 'shuffle_sort_start')
            update_job_sub_status(job_id, 0)
            initialize_shuffle_sort_phase(job_id, REDUCERS)
            

        else:
            # Raise
            update_job_sub_status(job_id, sub_status)

            
        
        return jsonify({"message": "Job mapping complete", "job_id": job_id}), 200


    except Exception as e:
        return jsonify({"message": "Error during map complete/initialize short", "job_id": job_id}), 200




@app.route('/shuffle_sort_complete', methods=['POST'])
def shuffle_sort_complete():
    data = request.json
    job_id = data.get('job_id')
    prefix = data.get('prefix')
    
    try:
        # Empty map_table
        empty_entries(MAP_TABLE, job_id)

        # Change status
        update_job_status(job_id, 'reduce_start')
        return jsonify({"message": "Job shuffle-sort complete", "job_id": job_id}), 200

    except Exception as e:
        return jsonify({"message": "Error during shuffle sort complete/initialize reduce", "job_id": job_id}), 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)



