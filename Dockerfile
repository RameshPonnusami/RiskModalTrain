# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# RUN sed -i 's|http://deb.debian.org/debian|http://ftp.us.debian.org/debian|g' /etc/apt/sources.list

# Install build tools and other necessary packages
RUN apt-get update

# Install any needed packages specified in requirements.txt

RUN python -m ensurepip --upgrade
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
# RUN pip install --upgrade setuptools
# RUN apt-get install gcc
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=run.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
