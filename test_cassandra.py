from cassandra.cluster import Cluster

# Connect to Cassandra (replace 'localhost' with your Cassandra service IP if not running locally)
cluster = Cluster(['83.212.78.127'], port=32000)
session = cluster.connect()

# Example: Create a keyspace
keyspace_name = "my_keyspace"
session.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace_name} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}};")

# Example: Create a table
table_name = "users"
session.execute(f"CREATE TABLE IF NOT EXISTS {keyspace_name}.{table_name} (user_id UUID PRIMARY KEY, name TEXT, age INT);")

# Example: Insert data into the table
user_id = uuid.uuid4()
name = "John Doe"
age = 30
session.execute(f"INSERT INTO {keyspace_name}.{table_name} (user_id, name, age) VALUES (%s, %s, %s);", (user_id, name, age))

# Example: Query data from the table
rows = session.execute(f"SELECT * FROM {keyspace_name}.{table_name};")
for row in rows:
    print(row.user_id, row.name, row.age)

# Close the session and cluster connection
session.shutdown()
cluster.shutdown()
