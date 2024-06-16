# Use the official Python image as a base image
FROM python:3.10.12

# Set the working directory in the container
WORKDIR /auth_service

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/auth_service/src

# Copy the requirements file into the container
COPY src/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory into the container
COPY src/ ./src/

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Copy the entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /entrypoint.sh

# Use the entrypoint script to run the FastAPI application and initialize the admin user
ENTRYPOINT ["/entrypoint.sh"]

