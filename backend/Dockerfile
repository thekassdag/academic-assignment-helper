# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the backend directory
COPY backend/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the data directory from the project root into the container's /app/data
COPY ./data /app/data

# Copy the rest of the backend source code into the container
# This ensures main.py and other modules are available even without a volume mount
COPY backend/ /app/


# Command to run the application using the absolute path
CMD ["python3", "/app/main.py"]
