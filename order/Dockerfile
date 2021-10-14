FROM python:3.6

ADD ./order/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

ENTRYPOINT gunicorn -b 0.0.0.0:8000  app:app
