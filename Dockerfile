# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  gcc libffi-dev libssl-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the relevant folders to container
COPY src/wordzilla/ ./wordzilla
COPY data_etl ./data_etl
COPY conf /conf
