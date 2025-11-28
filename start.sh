#!/usr/bin/env bash
set -o errexit

# 1. Ejecutar la Migración
python manage.py migrate --no-input

echo "Cargando datos iniciales de prueba usando runscript..."
python manage.py runscript load_menu 


gunicorn --bind 0.0.0.0:$PORT config.wsgi:application