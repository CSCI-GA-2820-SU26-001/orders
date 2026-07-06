FROM python:3.12-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system

COPY wsgi.py .
COPY service/ ./service/

RUN useradd --uid 1000 flask && chown -R flask /app
USER flask

ENV FLASK_APP=wsgi:app
ENV PORT=8080
EXPOSE $PORT

ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]