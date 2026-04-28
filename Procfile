web: gunicorn loja.wsgi:application --bind 0.0.0.0:$PORT
web: python manage.py migrate --noinput && gunicorn loja.wsgi:application --bind 0.0.0.0:$PORT