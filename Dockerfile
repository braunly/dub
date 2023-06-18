FROM python:3.10-slim-buster

RUN apt-get update && apt-get install --no-install-recommends -y build-essential libssl-dev zlib1g-dev gcc swig && rm -rf /var/lib/apt/lists/*

ENV WORKERS 5
ENV WORKER_THREADS 2

WORKDIR /app
COPY ./requirements /app/requirements
RUN pip install -r requirements/prod.txt
COPY . /app

CMD exec uwsgi \
  --hook-master-start "unix_signal:15 gracefully_kill_them_all" \
  --wsgi wsgi:app \
  --master \
  --die-on-term \
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
