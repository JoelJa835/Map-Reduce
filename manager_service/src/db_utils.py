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


def update_job_chunks(job_id, num_chunks):
    update_query = """
        UPDATE jobs SET number_of_chunks = %s WHERE job_id = %s
    """
    try:
        # Convert job_id to UUID type if it's not already
        if not isinstance(job_id, uuid.UUID):
            job_id = uuid.UUID(job_id)
        
        session.execute(update_query, (num_chunks, job_id))
    except Exception as e:
        logging.error(f"Failed to update job status in Cassandra: {e}")
        raise


def update_job_sub_status(job_id, sub_status):
    update_query = """
        UPDATE jobs SET sub_status = %s WHERE job_id = %s
    """
    try:
        # Convert job_id to UUID type if it's not already
        if not isinstance(job_id, uuid.UUID):
            job_id = uuid.UUID(job_id)
        
        session.execute(update_query, (sub_status, job_id))
    except Exception as e:
        logging.error(f"Failed to update job status in Cassandra: {e}")
        raise


def get_job_status_and_chunk(job_id):
    """
    Retrieves sub_status and number_of_chunks from Cassandra for a given job_id.
    Returns a tuple (sub_status, num_chunks).
    """
    select_query = """
        SELECT sub_status, number_of_chunks FROM jobs WHERE job_id = %s
    """
    try:
        # Convert job_id to UUID type if it's not already
        if not isinstance(job_id, uuid.UUID):
            job_id = uuid.UUID(job_id)
        
        result = session.execute(select_query, (job_id,))
        row = result.one()
        
        if row:
            return row.sub_status, row.number_of_chunks
        else:
            return None, None
    except Exception as e:
        logging.error(f"Failed to fetch job status and chunks from Cassandra: {e}")
        raise

def create_table_if_not_exists():
    keyspace_metadata = session.cluster.metadata.keyspaces.get('admins')
    if keyspace_metadata is None:
        raise ValueError("Keyspace does not exist")

    if 'intermediate_data' not in keyspace_metadata.tables:
        session.execute(f"""
        CREATE TABLE intermediate_data (
            job_id UUID,
            key TEXT,
            value TEXT,
            unique_id UUID,
            PRIMARY KEY (job_id, key, unique_id)
        );
        """)
   
