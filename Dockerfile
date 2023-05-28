# Use an official Python runtime as the base image
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Install xlwings and quantlib
RUN pip install xlwings quantlib

# Copy your Python application code to the container
COPY . /app

# Set the entry point to your Python script
CMD ["python", "quickstart.py"]