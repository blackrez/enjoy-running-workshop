FROM python:3.7-buster



COPY app.py requirements.txt /app/

RUN mkdir -p /tmp/img/ && \
	mkdir -p /app/html && \
	pip install -r /app/requirements.txt
COPY html/index.html /app/html/
WORKDIR /app/
CMD gunicorn --workers=2 --threads=4 --worker-class=gthread --bind 0.0.0.0:8080 app:app
EXPOSE 8080
