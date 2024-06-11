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
@click.argument('mapper_func', type=click.File('r'))
@click.argument('reducer_func', type=click.File('r'))
@click.argument('input_file', type=click.File('r'))
def submit(mapper_func, reducer_func, input_file):
    """Submit a new job."""
    token = get_token()
    if not token:
        click.echo("You are not logged in.")
        return
    # Read the contents of the mapper function
    mapper_code = mapper_func.read()

    # Read the contents of the reducer function
    reducer_code = reducer_func.read()

    # Read the contents of the input file (assumed to be JSON)
    input_data = json.load(input_file)

    # Prepare request payload
    payload = {
        "mapper_func": mapper_code,
        "reducer_func": reducer_code,
        "input_data": input_data
    }

    # Make HTTP POST request to submit job
    response = requests.post(SERVICE_URL, json=payload, headers={"Authorization": token})

    if response.status_code == 200:
        click.echo("Job submitted successfully.")
        click.echo(response.json())
    else:
        click.echo("Failed to submit job.")
        click.echo(response.text)



@jobs.command()
@click.argument('job_id')
def status(job_id):
    """View the status of an existing job."""
    token = get_token()
    if not token:
        click.echo("You are not logged in.")
        return
    # Make HTTP GET request to get job status
    response = requests.get(f"{SERVICE_URL}/jobs/status/{job_id}", headers={"Authorization": token})

    if response.status_code == 200:
        click.echo(response.json())
    else:
        click.echo("Failed to get job status.")
        click.echo(response.text)




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
