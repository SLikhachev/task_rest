# start flask app in gunicorn server
# recommended for test and production env depends of *.conf.py
#
# Preffered way to start is to mke use of a systemd service unit
#
#gunicorn --conf gunicorn.local.conf.py
gunicorn --conf gunicorn.zerodemo_local.conf.py