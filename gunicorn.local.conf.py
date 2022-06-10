import multiprocessing

bind= "127.0.0.1:8787"
workers= multiprocessing.cpu_count() * 2 + 1
wsgi_app= "main:application"
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
"DB_HOST=127.0.0.1",
"DB_NAME=zerodemo",
"DB_USER=zauther",
"DB_PASSWORD=borgen_boruh",
"DB_SCHEMA=webz",
"DB_AUTH=yes",
"FALSK_ENV=development"
]