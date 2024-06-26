from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging
import uuid

CASSANDRA_KEYSPACE = "admins"
MAP_TABLE = 'map_table'
SHUFFLE_TABLE = 'shuffle_table'
REDUCE_TABLE = 'reduce_table'


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


# def create_table_if_not_exists():
#     try :
#         session.execute(f"""
#         CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{MAP_TABLE} (
#             job_id UUID,
#             key TEXT,
#             value TEXT,
#             unique_id UUID,
#             PRIMARY KEY (job_id, key, unique_id)
#         );
#         """)
#     except Exception as e:
#         logging.error(f"Failed to create table in Cassandra: {e}")
#         raise

def insert_batch(batch):
    try:
        session.execute(batch)
        logging.info("Batch insertion successful")
    except Exception as e:
        logging.error(f"Failed to insert batch into Cassandra: {e}")
        raise

def insert_word(job_id, word, count, batch_number):
    try :
        session.execute(
                f"""
                INSERT INTO {MAP_TABLE} (job_id, batch_number, key, value) VALUES (%s, %s, %s, %s)
                """,
                (uuid.UUID(str(job_id)), str(batch_number), word, count)
            )
    except Exception as e:
        logging.error(f"Failed to insert entry in Cassandra: {e}")
        raise

def insert_shuffled(job_id, reducers_number, key, values):
    try :
        session.execute(
            f"""
            INSERT INTO {SHUFFLE_TABLE} (job_id, reducers_number, key, values) VALUES (%s, %s, %s, %s)
            """,
            (uuid.UUID(str(job_id)), str(reducers_number), key, values)
        )
    except Exception as e:
        logging.error(f"Failed to insert entry in Cassandra: {e}")
        raise

def insert_reduced_data(job_id, key, value):
    try :
        session.execute(
            f"""
            INSERT INTO {REDUCE_TABLE} (job_id, key, value) VALUES (%s, %s, %s)
            """,
            (uuid.UUID(str(job_id)), key, value)
        )
    except Exception as e:
        logging.error(f"Failed to insert entry in Cassandra: {e}")
        raise


def get_rows(job_id):
    rows = session.execute(f"SELECT key, value FROM {MAP_TABLE} WHERE job_id = %s", (uuid.UUID(str(job_id)),))
    return rows


def get_shuffled_data(job_id, reducers_number):
    rows = session.execute(f"SELECT key, values FROM {SHUFFLE_TABLE} WHERE job_id = %s AND reducers_number = %s", (uuid.UUID(str(job_id)), str(reducers_number)))
    return rows


def get_reduced_data(job_id):
    rows = session.execute(f"SELECT key, value FROM {REDUCE_TABLE} WHERE job_id = %s", (uuid.UUID(str(job_id)),))
    return rows