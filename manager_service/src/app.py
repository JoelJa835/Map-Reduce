from flask import Flask, request, jsonify
import logging
from utils import initiate_split_job, initialize_map_phase, initialize_shuffle_sort_phase, initialize_reduce_phase, initialize_combining_phase, save_job_id, load_job_id
from db_utils import update_job_status, update_job_chunks, get_job_status_and_chunk, update_job_sub_status, empty_entries, get_job_status, get_job_input_file
from minio_utils import delete_chunk


app = Flask(__name__)

NUM_CHUNKS = 10
REDUCERS = 2


MAP_TABLE = 'map_table'
SHUFFLE_TABLE = 'shuffle_table'
REDUCE_TABLE = 'reduce_table'

@app.route('/initialize_job', methods=['POST'])
def initialize_job():
    data = request.json
    job_id = data.get('job_id')
    filename = data.get('input_file')
    save_job_id(job_id)
    

    if not job_id or not filename:
        return jsonify({"error": "Missing required fields (job_id, filename)"}), 400

    try:
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
    save_job_id(job_id)

    try:
        # Verify chunks exist in Minio
        initialize_map_phase(job_id, NUM_CHUNKS)
        # Initialize the map phase
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
    save_job_id(job_id)

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
    reducers = data.get('reducers')
    save_job_id(job_id)
    
    try:
        # Empty map_table
        initialize_reduce_phase(job_id, reducers)
        

        

        return jsonify({"message": "Job shuffle-sort complete", "job_id": job_id}), 200

    except Exception as e:
        return jsonify({"message": "Error during shuffle sort complete/initialize reduce", "job_id": job_id}), 200


@app.route('/reduce_complete', methods=['POST'])
def reduce_complete():
    data = request.json
    job_id = data.get('job_id')
    prefix = data.get('prefix')
    save_job_id(job_id)

    try:
        sub_status, num_chunks = get_job_status_and_chunk(job_id)

        sub_status = sub_status + 1
        if sub_status == num_chunks:
            initialize_combining_phase(job_id)
            # End of reduce phase
            # Change status
            # Initialize combining phase
            
      
        else:
            # Raise
            update_job_sub_status(job_id, sub_status)
        return jsonify({"message": "Job reduce complete", "job_id": job_id}), 200

    except Exception as e:
        return jsonify({"message": "Error during reducer complete/initialize combining", "job_id": job_id}), 200


@app.route('/combine_complete', methods=['POST'])
def combinging_complete():
    data = request.json
    job_id = data.get('job_id')
    prefix = data.get('prefix')
    filename = data.get('file_name')
    save_job_id(job_id)

    try:
        sub_status, num_chunks = get_job_status_and_chunk(job_id)

        sub_status = sub_status + 1
        if sub_status == num_chunks:
            # End of reduce phase
            # Change status
            # Empty shuffle_table
            empty_entries(REDUCE_TABLE, job_id)            
            # Initialize combining phase
            update_job_chunks(job_id, 0)
            update_job_status(job_id, f"COMPLETED ({filename})")
            
      
        else:
            # Raise
            update_job_sub_status(job_id, sub_status)
        return jsonify({"message": "Job complete", "job_id": job_id}), 200

    except Exception as e:
        return jsonify({"message": "Error during combining complete", "job_id": job_id}), 200




@app.before_first_request
def on_start():
    # Get the previous job
    job_id = load_job_id()
    if job_id is not None:
        status = get_job_status()
        if status == 'SPLITTING_PHASE':
            file = get_job_input_file(job_id)
            initiate_split_job(job_id, file, NUM_CHUNKS)
        elif status == 'MAPPING_PHASE':
            initialize_map_phase(job_id, NUM_CHUNKS)
        elif status == 'SHUFFLE_AND_SORT_PHASE':
            initialize_shuffle_sort_phase(job_id, REDUCERS)
        elif status == 'REDUCE_PHASE':
            initialize_reduce_phase(job_id, REDUCERS)
        elif status == 'COMBINING_PHASE':
            initialize_combining_phase(job_id)
        

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)




