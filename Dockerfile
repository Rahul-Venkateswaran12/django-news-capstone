# Use Python base
FROM python:3.10-slim-bookworm

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install MariaDB server & client + build deps for mysqlclient
RUN apt-get update && \
    apt-get install -y mariadb-server mariadb-client \
    default-libmysqlclient-dev libmariadb-dev pkg-config gcc \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the project into the image
COPY . /app

# Expose Django default port
EXPOSE 8000

# Start MariaDB, create database, run migrations, and start Django dev server
CMD ["sh", "-c", "service mariadb start && mariadb -u root -e 'CREATE DATABASE IF NOT EXISTS news_db;' && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]

