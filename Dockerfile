FROM python:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /transcendence

RUN apt update && apt upgrade -y

COPY requirements.txt .
COPY manage.py .

RUN python3 -m venv venv
RUN venv/bin/pip3 install --upgrade pip
RUN venv/bin/pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8080

# Commande pour démarrer le serveur Redis et l'application Django
CMD service redis-server start && python manage.py runserver 0.0.0.0:8000