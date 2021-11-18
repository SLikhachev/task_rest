
#DOCKER_BUILDKIT=1
FROM python:3.6-slim-buster as build

RUN apt-get update \
    && apt-get -y install gcc libpq-dev 

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"    

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ADD ./static/pkg/barsxml-0.1.21.tar.gz .
RUN pip install --no-deps ./barsxml-0.1.21

FROM python:3.6-slim-buster as runtime
RUN apt-get update && \
    apt-get -y install --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
WORKDIR /opt/venv/app
COPY . /opt/venv/app

## add user
#RUN addgroup --system task && adduser --system --no-create-home --group task
#RUN chown -vR task:task /opt/venv/app && chmod -R 755 /opt/venv/app

#USER task

## set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8787

CMD ["gunicorn", "--conf", "gunicorn_conf.py", "--bind", "0.0.0.0:8787",  "main:app"]


