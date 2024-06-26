import logging
import os
from utils import split_file, map_file, shuffle_in_database, reduce_file, combining_reduced_data


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

def reduce(job_id, reducer):
    try:
        reduce_file(job_id, reducer)
    except Exception as e:
        logging.error(f"Failed to execute job: {e}")
        raise

def combine(job_id):
    try:
        combining_reduced_data(job_id)
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
        pass
    elif function_name == "MAP":
        job_id = os.getenv("JOB_ID")
        filename = os.getenv("FILENAME")
        number = os.getenv("NUMBER")
        map(job_id, filename, number)
        pass
    elif function_name == "REDUCE":
        job_id = os.getenv("JOB_ID")
        reducer = os.getenv("REDUCER")
        reduce(job_id, reducer)
        pass
    elif function_name == "SHUFFLESORT":
        job_id = os.getenv("JOB_ID")
        reducers = os.getenv("REDUCERS")
        shuffle_and_short(job_id, int(reducers)) 
        pass
    elif function_name == "COMBINING":
        job_id = os.getenv("JOB_ID")
        combine(job_id)
        pass
    else:
        logging.error(f"Unknown function name: {function_name}")

if __name__ == "__main__":
    main()
