from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
from minio_utils import get_chunk_names, create_minio_bucket
import traceback
import re
from db_utils import create_table_if_not_exists

# Assuming you are using in-cluster configuration, otherwise use config.load_kube_config()
config.load_incluster_config()



create_table_if_not_exists()

def initiate_split_job(job_id, filename, num_chunks):
    '''
        Creates a split job
    '''
    try:
        batch_v1 = client.BatchV1Api()

        # Prepare payload for Kubernetes job
        job_payload = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"split-job-{job_id}",  # Use a unique job name
                "namespace": "dena"
            },
            "spec": {
                "ttlSecondsAfterFinished": 30,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",  # Replace with your worker image
                            "imagePullPolicy": "Always",
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "SPLIT"},
                                {"name": "JOB_ID", "value": job_id},
                                {"name": "FILENAME", "value": filename},
                                {"name": "NUM_CHUNKS", "value": str(num_chunks)}
                            ]
                        }],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        # Create the Kubernetes job
        created_job = batch_v1.create_namespaced_job(namespace="dena", body=job_payload)
        logging.info(f"Job {created_job.metadata.name} created successfully.")
        return True

    except ApiException as e:
        logging.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e.reason}")
        return False

    except Exception as e:
        logging.error(f"Failed to initiate split job: {e}")
        return False

# Example usage:
# initiate_split_job("123456", "example.txt", 10)


def initialize_map_phase(job_id):
    '''
        Initializes map phase
    '''

    create_table_if_not_exists()
    # First retrieve all chucknames relative to the job_id from bucket
    chunk_names = get_chunk_names(job_id)

    # Get the last job sub status
    
    for chunk_name in chunk_names:
        create_map_job(job_id, chunk_name)
    





def create_map_job(job_id, chunk_name):
    '''
        Creates a map job
    '''


    # Get the number of the chunk from chunk name
    chunk_number = get_chunk_number(chunk_name)
    try:
        batch_v1 = client.BatchV1Api()

        # Prepare payload for Kubernetes job
        job_payload = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"map-{job_id}-{chunk_number}",  # Unique job name
                "namespace": "dena"
            },
            "spec": {
                "ttlSecondsAfterFinished": 30,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",
                            "imagePullPolicy": "Always",
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "MAP"},
                                {"name": "JOB_ID", "value": str(job_id)},
                                {"name": "FILENAME", "value": chunk_name},
                                {"name": "NUMBER", "value": str(chunk_number)},
                            ]
                        }],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        # Create the Kubernetes job
        created_job = batch_v1.create_namespaced_job(namespace="dena", body=job_payload)
        logging.info(f"Job {created_job.metadata.name} created successfully.")
        return True

    except ApiException as e:
        logging.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e.reason}")
        return False

    except Exception as e:
        logging.error(f"Failed to initiate map job: {e}")
        return False



def get_chunk_number(chunk_name):
    '''
    Extracts the chunk number from the chunk name.
    '''
    try:
        # Assuming the chunk_name format is "job-{job_id}/chunk-{i}"
        match = re.search(r'chunk-(\d+)', chunk_name)
        if match:
            return int(match.group(1))
        else:
            raise ValueError(f"Invalid chunk name format: {chunk_name}")
    except Exception as e:
        print(f"Error occurred while extracting chunk number: {e}")
        traceback.print_exc()
        return None



def initialize_shuffle_sort_phase(job_id, reducers):
    '''
        Creates a shuffle_sort job
    '''
    create_table_if_not_exists()

    try:
        batch_v1 = client.BatchV1Api()

        # Prepare payload for Kubernetes job
        job_payload = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"shuffle-sort-{job_id}",  # Use a unique job name
                "namespace": "dena"
            },
            "spec": {
                "ttlSecondsAfterFinished": 30,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",  # Replace with your worker image
                            "imagePullPolicy": "Always",
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "SHUFFLESORT"},
                                {"name": "JOB_ID", "value": job_id},
                                {"name": "REDUCERS", "value": str(reducers)},
                            ]
                        }],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        # Create the Kubernetes job
        created_job = batch_v1.create_namespaced_job(namespace="dena", body=job_payload)
        logging.info(f"Job {created_job.metadata.name} created successfully.")
        return True

    except ApiException as e:
        logging.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e.reason}")
        return False

    except Exception as e:
        logging.error(f"Failed to initiate shuffle_sort job: {e}")
        return False



def create_reduce_job(job_id, reducer):
    '''
        Creates a reduce job
    '''

    try:
        batch_v1 = client.BatchV1Api()

        # Prepare payload for Kubernetes job
        job_payload = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"reduce-{job_id}-{reducer}",  # Use a unique job name
                "namespace": "dena"
            },
            "spec": {
                "ttlSecondsAfterFinished": 30,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",  # Replace with your worker image
                            "imagePullPolicy": "Always",
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "REDUCE"},
                                {"name": "JOB_ID", "value": job_id},
                                {"name": "REDUCER", "value": str(reducer)},
                            ]
                        }],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        # Create the Kubernetes job
        created_job = batch_v1.create_namespaced_job(namespace="dena", body=job_payload)
        logging.info(f"Job {created_job.metadata.name} created successfully.")
        return True

    except ApiException as e:
        logging.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e.reason}")
        return False

    except Exception as e:
        logging.error(f"Failed to initiate reducer job: {e}")
        return False




def initialize_reduce_phase(job_id, reducers):
    '''
        Initializes reduce phase
    '''
    create_table_if_not_exists()

    for i in range(reducers):
        create_reduce_job(job_id, i)
    


def initialize_combining_phase(job_id):
    '''
        Initializes combining phase
    '''

    create_minio_bucket()

    try:
        batch_v1 = client.BatchV1Api()

        # Prepare payload for Kubernetes job
        job_payload = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"combine-{job_id}",  # Use a unique job name
                "namespace": "dena"
            },
            "spec": {
                "ttlSecondsAfterFinished": 30,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",  # Replace with your worker image
                            "imagePullPolicy": "Always",
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "COMBINING"},
                                {"name": "JOB_ID", "value": job_id},
                            ]
                        }],
                        "restartPolicy": "OnFailure"
                    }
                }
            }
        }

        # Create the Kubernetes job
        created_job = batch_v1.create_namespaced_job(namespace="dena", body=job_payload)
        logging.info(f"Job {created_job.metadata.name} created successfully.")
        return True

    except ApiException as e:
        logging.error(f"Exception when calling BatchV1Api->create_namespaced_job: {e.reason}")
        return False

    except Exception as e:
        logging.error(f"Failed to initiate combining job: {e}")
        return False