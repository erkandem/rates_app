# rates_app

web: uwsgi --wsgi-file wsgi.py --http-socket :$(PORT)