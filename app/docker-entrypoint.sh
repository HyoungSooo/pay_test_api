#!/bin/bash

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "MySQL started"
fi

# Décommenter pour supprimer la bdd à chaque redémarrage (danger)
# echo "Clear entire database"
# python manage.py flush --no-input

echo "Appling database migrations..."
python manage.py makemigrations 
python manage.py migrate
python manage.py change_database_charactor_set
python manage.py test
python manage.py create_sample_data

exec "$@"
