from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging
import uuid


# Cassandra connection setup
contact_points = ['cassandra-0.cassandra.dena.svc.cluster.local']  # Replace with your Cassandra service DNS
auth_provider = PlainTextAuthProvider(username='admin', password='admin')
keyspace = 'admins'  # Replace with your keyspace name

try:
    cluster = Cluster(contact_points=contact_points, auth_provider=auth_provider)
    session = cluster.connect(keyspace)
except Exception as e:
    logging.error(f"Failed to connect to Cassandra: {e}")
    raise

def update_job_status(job_id, status):
    update_query = """
        UPDATE jobs SET status = %s WHERE job_id = %s
    """
    try:
        # Convert job_id to UUID type if it's not already
        if not isinstance(job_id, uuid.UUID):
            job_id = uuid.UUID(job_id)
        
        session.execute(update_query, (status, job_id))
    except Exception as e:
        logging.error(f"Failed to update job status in Cassandra: {e}")
        raise
