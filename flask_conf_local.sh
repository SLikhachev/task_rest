# ENV variables for local run with some "dbnae" DB

# source flask_conf.sh
export FLASK_ENV='development'
export FLASK_APP='run.py'
export DB_HOST='127.0.0.1'
export DB_NAME='dbname'
export DB_USER='dbuser'
export DB_PASSWORD='dbpassword'
export DB_SCHEMA='dbschema'
export DB_AUTH='yes'
export JWT_TOKEN_SECRET="Some token for JWT authentication"