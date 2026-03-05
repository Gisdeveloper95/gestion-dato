#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté disponible..."

# Esperar a que PostgreSQL esté listo
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "PostgreSQL no está listo - esperando..."
  sleep 2
done

echo "PostgreSQL está listo!"

# Ejecutar migraciones
echo "Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear || true

# Crear superusuario si no existe (opcional)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

echo "Iniciando servidor Django..."
exec "$@"
