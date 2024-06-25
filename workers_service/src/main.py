import logging
import os
from utils import split_file, map_file, shuffle_in_database


def split(job_id, filename, num_chunks):
    try:
        split_file(job_id, filename, num_chunks)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise


def map(job_id, filename, number):
    try:
        map_file(job_id, filename, number)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise


def shuffle_and_short(job_id, reducers):
    try:
        shuffle_in_database(job_id, reducers)
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
        number = os.getenv("NUMBER")
        map(job_id, filename, number)
        pass
    elif function_name == "REDUCE":
        # Implement logic for REDUCE function
        pass
    elif function_name == "SHUFFLESORT":
        job_id = os.getenv("JOB_ID")
        reducers = os.getenv("REDUCERS")
        shuffle_and_short(job_id, int(reducers))
        pass
    else:
        logging.error(f"Unknown function name: {function_name}")

if __name__ == "__main__":
    main()
