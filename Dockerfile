# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_app.py

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY web_app.py .
COPY templates/ templates/
COPY static/ static/

# Make port 5000 available
EXPOSE 5000

# Run Flask directly for simplicity
CMD ["flask", "run", "--host=0.0.0.0"]
