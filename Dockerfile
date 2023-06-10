# Use an official Python runtime as the base image
FROM python:3.10

# Makes sure that logs are shown immediately
ENV PYTHONUNBUFFERED=1

# Install system dependencies for QuantLib
RUN apt-get update && apt-get install -y \
    libboost-python-dev \
    libboost-thread-dev \
    libboost-system-dev \
    libboost-serialization-dev \
    libboost-filesystem-dev \
    libboost-test-dev \
    libboost-regex-dev \
    libboost-iostreams-dev \
    cmake

# Download and build QuantLib from source
RUN wget https://github.com/lballabio/QuantLib/releases/download/QuantLib-v1.30/QuantLib-1.30.tar.gz && \
    tar -xvf QuantLib-1.30.tar.gz && \
    cd QuantLib-1.30 && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr .. && \
    make -j $(nproc) && \
    make install

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
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
