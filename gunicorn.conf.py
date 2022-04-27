import multiprocessing

bind= "127.0.0.1:8787"
workers= multiprocessing.cpu_count() * 2 + 1
wsgi_app= "main:application"
reload= True
loglevel = "info"
errorlog = "/home/aughing/www/zeroms.site/logs/task_rest/errors.log"  # "-" stderr
accesslog = "/home/aughing/www/zeroms.site/logs/task_rest/access.log"  # "-" stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
threads = 3
raw_env = [
"DB_PORT=5432",
"DB_HOST=127.0.0.1",
"DB_NAME=hokuto",
"DB_USER=postgres",
"DB_PASSWORD=boruh",
"DB_SCHEMA=public",
"DB_AUTH=no"
]