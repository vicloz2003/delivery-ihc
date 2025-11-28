#!/usr/bin/env bash
set -o errexit

# 1. Ejecutar la Migración (Crea las tablas en PostgreSQL)
echo "Aplicando migraciones a la Base de Datos..."
python manage.py migrate --no-input

# 2. Cargar Datos Iniciales (Pobla las tablas con el menú)
echo "Cargando datos iniciales de prueba..."
python scripts/create_initial_data.py

# 3. Iniciar el Servidor Gunicorn
echo "Iniciando el servidor Gunicorn..."
gunicorn --bind 0.0.0.0:$PORT config.wsgi:application