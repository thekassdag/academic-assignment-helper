# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the mounted backend directory
COPY backend/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the data directory from the project root into the container's /app/data
# The build context is the project root, so ./data refers to the host's data directory
COPY ./data /app/data

# Command to run the application
# main.py is directly in /app due to the volume mount
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
