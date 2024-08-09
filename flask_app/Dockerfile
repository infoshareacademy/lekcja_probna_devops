# Use the official Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Flask and other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the application runs on
EXPOSE 5000

# Define the command to run the application
ENTRYPOINT ["python", "app.py"]
