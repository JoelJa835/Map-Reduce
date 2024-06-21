from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import uuid

# Connect to Cassandra
contact_points = ['83.212.78.127']  # Replace with your Cassandra service IP
port = 32000
auth_provider = PlainTextAuthProvider(username='admin', password='admin')  # Replace with your Cassandra admin username and password
cluster = Cluster(contact_points=contact_points, port=port, auth_provider=auth_provider)
session = cluster.connect()

try:
    # Determine the number of nodes in the cluster
    metadata = cluster.metadata
    num_nodes = len(metadata.all_hosts())

    # Set replication factor to the number of nodes, but not less than 1
    replication_factor = max(1, num_nodes)
    
    # Create keyspace for admins
    keyspace_name = "admins"
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace_name}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': {replication_factor}}};
    """)

    # Connect to the keyspace
    session.set_keyspace(keyspace_name)

    # Create users table
    users_table = "users"
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {users_table} (
            user_id UUID PRIMARY KEY,
            username TEXT,
            password TEXT
        );
    """)

    # Insert admin user
    admin_user_id = uuid.uuid4()
    admin_username = "admin"
    admin_password = "admin"  # Replace with a secure password
    session.execute(f"""
        INSERT INTO {users_table} (user_id, username, password)
        VALUES (%s, %s, %s);
    """, (admin_user_id, admin_username, admin_password))

    # Create roles table
    roles_table = "roles"
    session.execute(f"""
        CREATE TABLE IF NOT EXISTS {roles_table} (
            role_name TEXT PRIMARY KEY,
            permissions SET<TEXT>
        );
    """)

    # Insert admin role with permissions
    admin_role_name = "admin"
    admin_role_permissions = {"CREATE", "ALTER", "DROP", "SELECT", "MODIFY"}  # Example permissions, adjust as needed
    session.execute(f"""
        INSERT INTO {roles_table} (role_name, permissions)
        VALUES (%s, %s);
    """, (admin_role_name, admin_role_permissions))

    print("Database initialization completed successfully.")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the session and cluster connection
    session.shutdown()
    cluster.shutdown()


