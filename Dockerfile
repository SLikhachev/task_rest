
FROM tiangolo/meinheld-gunicorn:python3.9-alpine3.13

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY .  /app


