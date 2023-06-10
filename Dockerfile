# Use an official Python runtime as the base image
FROM python:3.10

# Makes sure that logs are shown immediately
ENV PYTHONUNBUFFERED=1

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python application code to the container
COPY app /app

# Set the working directory to /app
WORKDIR /app

# For google sheets to query
EXPOSE 80

# This is for single-container deployments (multiple-workers)
CMD ["gunicorn", "main:app", \
     "--bind", "0.0.0.0:80", \
     "--access-logfile", "-", \
     "--workers", "2", \
     "--worker-class", "uvicorn.workers.UvicornWorker"]
