from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging
import uuid

CASSANDRA_KEYSPACE = "admins"
CASSANDRA_TABLE = "intermediate_data"
FINAL_RESULT_TABLE = "final_results"


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


def create_table_if_not_exists():
    try :
        session.execute(f"""
        CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
            job_id UUID,
            key TEXT,
            value TEXT,
            unique_id UUID,
            PRIMARY KEY (job_id, key, unique_id)
        );
        """)
    except Exception as e:
        logging.error(f"Failed to create table in Cassandra: {e}")
        raise

def insert_batch(batch):
    try:
        session.execute(batch)
        logging.info("Batch insertion successful")
    except Exception as e:
        logging.error(f"Failed to insert batch into Cassandra: {e}")
        raise

