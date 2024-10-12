# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for dlib and OpenCV
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    libboost-python-dev \
    python3-dev \
    python3-pip \
    libatlas-base-dev \
    libboost-thread-dev \
    libboost-system-dev

# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port Flask runs on
EXPOSE 5000

# Set the default command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
