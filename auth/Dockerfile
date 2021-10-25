FROM python:3.6
ADD ./client/requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT gunicorn -b 0.0.0.0:8000 app:app
