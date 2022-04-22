import multiprocessing

bind= "127.0.0.1:8787"
workers= multiprocessing.cpu_count() * 2 + 1
wsgi_app= "main:application"
reload= True
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
threads = 3