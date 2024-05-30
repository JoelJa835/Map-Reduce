import click

"""
    User interface 
"""


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
    # Read the contents of the mapper function
    mapper_code = mapper_func.read()

    # Read the contents of the reducer function
    reducer_code = reducer_func.read()

    # Read the contents of the input file (assumed to be JSON)
    input_data = json.load(input_file)

    # Placeholder for actual job submission logic
    click.echo("Job submitted successfully.")
    click.echo("Mapper function:")
    click.echo(mapper_code)
    click.echo("Reducer function:")
    click.echo(reducer_code)
    click.echo("Input data:")
    click.echo(input_data)

    """
    Submit job logic
    """



@jobs.command()
@click.argument('job_id')
def status(job_id):
    """View the status of an existing job."""
    # Dummy status for illustration
    status = "running"  # In real implementation, this would query the job's status
    click.echo(f"Status of job '{job_id}': {status}")
    """
    Get status of a job logic
    """




# Admin command group
@click.group()
def admin():
    """Administer the system."""
    pass

@admin.command()
@click.argument('username')
def create_user(username):
    """Create a new user."""
    click.echo(f"Creating user '{username}'...")
    while True:
        password1 = click.prompt('Enter password', hide_input=True)
        password2 = click.prompt('Confirm password', hide_input=True)
        if password1 == password2:
            break
        else:
            click.echo("Passwords do not match. Please try again.")
    
    """
    Create user logic
    """
    click.echo(f"User '{username}' created successfully.")


@admin.command()
@click.argument('username')
def delete_user(username):
    """Delete an existing user."""
    confirmation = click.confirm(f"Are you sure you want to delete user '{username}'?", default=False)
    if confirmation:
        click.echo(f"User '{username}' deleted successfully.")
    else:
        click.echo("Deletion canceled.")
    """
    Delete User logic
    """


"""
TODO manage the system logic
"""




# Define the login command
@click.command()
@click.option('--username', prompt=True, help='Your username')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
def login(username, password):
    """Log in to the system."""

    """
    Authentication Logic
    """
    
    click.echo("Auth")



# Define the main CLI group
@click.group()
def cli():
    """Main CLI for job and admin management."""
    pass

# Add the command groups to the main CLI group
cli.add_command(jobs)
cli.add_command(admin)
cli.add_command(login)


if __name__ == '__main__':
    cli()
