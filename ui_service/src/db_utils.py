from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging
import uuid

# Cassandra connection setup
contact_points = ['cassandra-0.cassandra.dena.svc.cluster.local']
auth_provider = PlainTextAuthProvider(username='admin', password='admin')
keyspace = 'admins'

try:
    cluster = Cluster(contact_points=contact_points, auth_provider=auth_provider)
    session = cluster.connect(keyspace)
except Exception as e:
    logging.error(f"Failed to connect to Cassandra: {e}")
    raise


def create_jobs_table(session):
    keyspace = session.cluster.metadata.keyspaces.get('admins')
    if keyspace is None:
        raise ValueError("Keyspace does not exist")

    if 'jobs' not in keyspace.tables:
        session.execute("""
            CREATE TABLE jobs (
                job_id UUID PRIMARY KEY,
                input_file TEXT,
                status TEXT
            )
        """)

def submit_job_to_cassandra(session, job_id, input_file):
    insert_query = """
        INSERT INTO jobs (job_id, input_file, status)
        VALUES (%s, %s, %s)
    """
    status = 'submitted'  # Initial status
    try:
        session.execute(insert_query, (job_id, input_file, status))
    except Exception as e:
        logging.error(f"Failed to insert job into Cassandra: {e}")
        raise


def get_job_status_from_cassandra(job_id):
    select_query = """
        SELECT * FROM jobs WHERE job_id = %s
    """
    try:
        result = session.execute(select_query, (job_id,))
        row = result.one()  # Assuming job_id is unique; use result if multiple rows expected
        if row:
            return {"job_id": str(row.job_id), "status": row.status}
        else:
            return None
    except Exception as e:
        logging.error(f"Failed to fetch job status from Cassandra: {e}")
        raise