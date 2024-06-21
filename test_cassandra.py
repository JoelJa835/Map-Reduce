from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid

# Connect to Cassandra (replace 'localhost' with your Cassandra service IP if not running locally)
contact_points = ['83.212.78.127']  # Replace with your Cassandra service IP
port = 32000
auth_provider = PlainTextAuthProvider(username='your_admin_username', password='your_admin_password')  # Replace with your Cassandra admin username and password
cluster = Cluster(contact_points=contact_points, port=port, auth_provider=auth_provider)
session = cluster.connect()

try:
    # Create keyspace for admins
    keyspace_name = "admins"
    session.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace_name} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}};")

    # Connect to the keyspace
    session.set_keyspace(keyspace_name)

    # Create users table
    table_name = "users"
    session.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (user_id UUID PRIMARY KEY, username TEXT, password TEXT);")

    # Insert admin user
    admin_user_id = uuid.uuid4()
    admin_username = "admin"
    admin_password = "admin"  # Replace with a secure password
    session.execute(f"INSERT INTO {table_name} (user_id, username, password) VALUES (%s, %s, %s);", (admin_user_id, admin_username, admin_password))

    # Create roles table
    table_name = "roles"
    session.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (role_name TEXT PRIMARY KEY, permissions SET<TEXT>);")

    # Insert admin role with permissions
    admin_role_name = "admin"
    admin_role_permissions = {"CREATE", "ALTER", "DROP", "SELECT", "MODIFY"}  # Example permissions, adjust as needed
    session.execute(f"INSERT INTO {table_name} (role_name, permissions) VALUES (%s, %s);", (admin_role_name, admin_role_permissions))

    print("Database initialization completed successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the session and cluster connection
    session.shutdown()
    cluster.shutdown()

