import click
import requests
import os

"""
    User interface 
"""

SERVICE_URL = "http://localhost:8080"
token_file = "token.txt"

def get_token():
    try:
        with open(token_file, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        click.echo("Token file not found.")
        return None
    

def save_token(token):
    with open(token_file, "w") as file:
        file.write(token)

def delete_token():
    try:
        os.remove(token_file)
    except FileNotFoundError:
        pass



# Jobs command group
@click.group()
def jobs():
    """Manage jobs."""
    pass

@jobs.command()
@click.argument('input_name', type=str)
def submit(input_name):
    """Submit a new job."""
    token = get_token()  # Implement your token retrieval logic here
    if not token:
        click.echo("You are not logged in.")
        return

    # Placeholder for other inputs (mapper_func, reducer_func)
    mapper_code = ''
    reducer_code = ''

    # Prepare payload
    payload = {
        "mapper_func": mapper_code,
        "reducer_func": reducer_code,
        "input_file": input_name  # Assuming input_name is the name of the file to be submitted
    }

    # Make HTTP POST request to submit job
    headers = {"Authorization": token, "Content-Type": "application/json"}
    response = requests.post(f"{SERVICE_URL}/jobs/submit", json=payload, headers=headers)

    if response.status_code == 200:
        click.echo("Job submitted successfully.")
        click.echo(response.json())
    else:
        click.echo(f"Failed to submit job. Status code: {response.status_code}")
        click.echo(response.text)



@jobs.command()
@click.argument('job_id')
def status(job_id):
    """View the status of an existing job."""
    token = get_token()
    if not token:
        click.echo("You are not logged in.")
        return

    headers = {"Authorization": token}
    try:
        response = requests.get(f"{SERVICE_URL}/jobs/status/{job_id}", headers=headers)
        if response.status_code == 200:
            job_status = response.json()
            sub_status = job_status.get('sub_status', 'N/A')
            number_of_chunks = job_status.get('number_of_chunks', 'N/A')
            click.echo(f"Job ID: {job_status['job_id']}, Status: {job_status['status']}, Substatus: {sub_status}/{number_of_chunks}")
        elif response.status_code == 404:
            click.echo("Job not found.")
        else:
            click.echo(f"Failed to get job status. Status code: {response.status_code}")
            click.echo(response.text)
    except requests.RequestException as e:
        click.echo(f"Failed to connect to server: {e}")



# Admin command group
@click.group()
def admin():
    """Administer the system."""
    pass

@admin.command()
@click.argument('username')
def create_user(username):
    token = get_token()
    if not token:
        click.echo("You are not logged in.")
        return
    """Create a new user."""
    # Prompt for password input
    while True:
        password1 = click.prompt('Enter password', hide_input=True)
        password2 = click.prompt('Confirm password', hide_input=True)
        if password1 == password2:
            break
        else:
            click.echo("Passwords do not match. Please try again.")

    # Prepare request payload
    payload = {"username": username, "password": password1, "email": f"{username}@example.com"}

    # Make HTTP POST request to create user
    response = requests.post(f"{SERVICE_URL}/admin/create_user", json=payload, headers={"Authorization": token})

    if response.status_code == 200:
        click.echo(f"User '{username}' created successfully.")
    else:
        click.echo("Failed to create user.")
        click.echo(response.text)






# @admin.command()
# @click.argument('username')
# def delete_user(username):
#     """Delete an existing user."""
#     confirmation = click.confirm(f"Are you sure you want to delete user '{username}'?", default=False)
#     if confirmation:
#         click.echo(f"User '{username}' deleted successfully.")
#     else:
#         click.echo("Deletion canceled.")
#     """
#     Delete User logic
#     """


# Logout command
@click.command()
def logout():
    """Log out of the system."""
    delete_token()
    click.echo("Logged out successfully.")

# Login command
@click.command()
@click.option('--username', prompt=True, help='Your username')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
def login(username, password):
    """Log in to the system."""
    token = get_token()
    if token:
        click.echo("You are already logged in. Please log out first.")
        return

    # Prepare request payload
    payload = {"username": username, "password": password}

    # Make HTTP POST request to login
    response = requests.post(f"{SERVICE_URL}/login", json=payload)

    if response.status_code == 200:
        # Save token to a file
        save_token(response.json()["access_token"])
        click.echo("Login successful.")
    else:
        click.echo("Login failed.")
        click.echo(response.text)


# Define the main CLI group
@click.group()
def cli():
    """Main CLI for job and admin management."""
    pass

# Add the command groups to the main CLI group
cli.add_command(jobs)
cli.add_command(admin)
cli.add_command(login)
cli.add_command(logout)

if __name__ == '__main__':
    cli()
