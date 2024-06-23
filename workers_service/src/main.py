# worker_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import uuid
import collections

app = FastAPI()

# Cassandra configuration
CASSANDRA_KEYSPACE = "mapreduce"
CASSANDRA_TABLE = "intermediate_data"
FINAL_RESULT_TABLE = "final_results"

# Update with the correct Cassandra host and port
contact_points = ['127.0.0.1']
port = 9042

# Cluster initialization
cluster = Cluster(contact_points=contact_points, port=port)
session = cluster.connect()

# Ensure keyspace and tables exist
session.execute(f"""
CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE}
WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }};
""")
session.execute(f"""
CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (
    job_id uuid,
    key text,
    value text,
    PRIMARY KEY (job_id, key, value)
);
""")
session.execute(f"""
CREATE TABLE IF NOT EXISTS {CASSANDRA_KEYSPACE}.{FINAL_RESULT_TABLE} (
    job_id uuid,
    key text,
    reduced_value text,
    PRIMARY KEY (job_id, key)
);
""")

class MapRequest(BaseModel):
    job_id: uuid.UUID
    data: list

class ShuffleSortRequest(BaseModel):
    job_id: uuid.UUID

class ReduceRequest(BaseModel):
    job_id: uuid.UUID
    key: str
    values: list

@app.post("/map/")
async def map_data(map_request: MapRequest):
    job_id = map_request.job_id
    data = map_request.data

    for item in data:
        for key, value in item.items():
            session.execute(
                f"INSERT INTO {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} (job_id, key, value) VALUES (%s, %s, %s)",
                (job_id, key, value)
            )

    return {"status": "success", "message": "Data mapped and stored in Cassandra"}

@app.post("/shuffle-sort/")
async def shuffle_sort(shuffle_sort_request: ShuffleSortRequest):
    job_id = shuffle_sort_request.job_id

    # Retrieve and sort data
    query = SimpleStatement(
        f"SELECT key, value FROM {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE} WHERE job_id=%s"
    )
    result = session.execute(query, (job_id,))

    sorted_data = collections.defaultdict(list)
    for row in result:
        sorted_data[row.key].append(row.value)

    return {"status": "success", "sorted_data": sorted_data}


@app.post("/reduce/")
async def reduce_data(reduce_request: ReduceRequest):
    job_id = reduce_request.job_id
    key = reduce_request.key
    values = reduce_request.values

    # Example reduce operation (concatenate values)
    reduced_value = ",".join(values)

    session.execute(
        f"INSERT INTO {CASSANDRA_KEYSPACE}.{FINAL_RESULT_TABLE} (job_id, key, reduced_value) VALUES (%s, %s, %s)",
        (job_id, key, reduced_value)
    )

    return {"status": "success", "message": "Data reduced and stored in Cassandra"}
