# Stage 1: Base dependencies
FROM ubuntu:20.04 AS base

# Set environment variables
ENV TZ=UTC
ENV DEBIAN_FRONTEND=noninteractive

# Install base system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.10 \
        python3-pip \
        python3-dev \
        build-essential \
        libpq-dev \
        libffi-dev \
        libssl-dev \
        tzdata \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Nginx (cached)
FROM base AS nginx-stage

RUN apt-get update
RUN apt-get install -y nginx

# Set the timezone (optional, adjust according to your needs)
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Stage 3: Application (no cache)
FROM nginx-stage AS app-stage

# Set the working directory in the container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements_.txt requirements_.txt
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements_.txt

# Copy the Flask app code into the container
COPY . .

# Expose the port that Flask runs on
EXPOSE 80

# Start Nginx and Flask
CMD  nginx -g "daemon off;" & python3 /app/run.py
