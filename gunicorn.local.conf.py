""" Gunicorn config for development

    Here we explicit declare the ENV variables, such as
    DB_*
    JWT_*

    This config created for example (temolate).
    For the tests you should replace ENV vars with actual values

    In production these vars should be configured in instance config file
    Prefferd way to start the app is make use of a systemd service unit

"""

import multiprocessing

bind= "127.0.0.1:8787"
workers= multiprocessing.cpu_count() * 2 + 1
wsgi_app= "wsgi:application"
reload= True
loglevel = "info"
errorlog = "-" #stderr
accesslog ="-" #stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
threads = 3
raw_env = [
"DB_PORT=5432",
"DB_HOST=192.168.0.31",
"DB_NAME=dbname",
"DB_USER=dbuser",
"DB_PASSWORD=dbpassword",
"DB_SCHEMA=dbschema",
"DB_AUTH=no",
"JWT_TOKEN_SECRET=Some JWT token secret"
]
