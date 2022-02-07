FROM python:3.9-slim-buster

RUN apt-get update && apt-get install --no-install-recommends -y build-essential zlib1g-dev gcc && rm -rf /var/lib/apt/lists/*

ENV WORKERS 5
ENV WORKER_THREADS 2

WORKDIR /app
COPY ./requirements /app/requirements
RUN pip install -r requirements/prod.txt
COPY . /app

CMD exec uwsgi \
  --wsgi dub.wsgi:app \
  --master \
  --socket 0.0.0.0:8080 \
  --processes $WORKERS \
  --threads $WORKER_THREADS \
  --buffer-size 16384 \
  --lazy-apps \
  --log-5xx \
  --log-slow 3000 \
  --log-ioerror \
  --log-x-forwarded-for \
  --thunder-lock \
  --max-requests 1000
