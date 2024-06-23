import logging
import os
from utils import split_file


def split(job_id, filename, num_chunks):
    try:
        split_file(job_id, filename, num_chunks)
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
        # Implement logic for MAP function
        pass
    elif function_name == "REDUCE":
        # Implement logic for REDUCE function
        pass
    else:
        logging.error(f"Unknown function name: {function_name}")

if __name__ == "__main__":
    main()
