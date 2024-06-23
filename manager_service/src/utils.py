from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging

# Assuming you are using in-cluster configuration, otherwise use config.load_kube_config()
config.load_incluster_config()

def initiate_split_job(job_id, filename, num_chunks):
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
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "worker",
                            "image": "gsiatras13/map-reduce-worker:latest",  # Replace with your worker image
                            "env": [
                                {"name": "FUNCTION_NAME", "value": "SPLIT"},
                                {"name": "JOB_ID", "value": job_id},
                                {"name": "FILENAME", "value": filename},
                                {"name": "NUM_CHUNKS", "value": str(num_chunks)}
                            ]
                        }],
                        "restartPolicy": "Never"
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
