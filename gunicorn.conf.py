""" Gunicorn config for production

    Any ENV variables should be placed in ./instance/configs.py

    Recommended way to start app is with help of a systemd service's unit

"""

import multiprocessing

bind= "127.0.0.1:8787"
workers= multiprocessing.cpu_count() * 2 + 1
wsgi_app= "wsgi:application"
reload= True
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
worker_tmp_dir = "/dev/shm"
graceful_timeout = 120
timeout = 120
keepalive = 5
threads = 3