import logging
import os
from utils import split_file, map_file


def split(job_id, filename, num_chunks):
    try:
        split_file(job_id, filename, num_chunks)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise


def map(job_id, filename):
    try:
        map_file(job_id, filename)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise


def shuffle_and_short(job_id):
    try:
        shuffle_in_databse(job_id)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise




# Entry point for Kubernetes Job or standalone execution
def main():
    function_name = os.getenv("FUNCTION_NAME")

    if function_name == "SPLIT":
        job_id = os.getenv("JOB_ID")
        filename = os.getenv("FILENAME")
        num_chunks = int(os.getenv("NUM_CHUNKS"))
        split(job_id, filename, num_chunks)
    elif function_name == "MAP":
        job_id = os.getenv("JOB_ID")
        filename = os.getenv("FILENAME")
        map(job_id, filename)
        pass
    elif function_name == "REDUCE":
        # Implement logic for REDUCE function
        pass
    elif function == "SHUFFLESORT":
        job_id = os.getenv("JOB_ID")
        shuffle_and_short(job_id)
        pass
    else:
        logging.error(f"Unknown function name: {function_name}")

if __name__ == "__main__":
    main()
