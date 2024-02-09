# run this script in development mode
# firstly sh flask/flask_conf_hokuto[zerodemo].sh  for set ENV vars
#
# $ sh flask_conf_local.sh
# here "flask_conf_*.sh" contains an actual environment's variables
#
# then
# $ sh runs.sh
#
# static data will be write to webapp/static/data/reestr
#
python -m flask run --port 8787