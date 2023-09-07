FROM python:3.9.5-slim-buster
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2
ENV APP_VERSION=0.1
WORKDIR /python-docker
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py", "--host=0.0.0.0"]
