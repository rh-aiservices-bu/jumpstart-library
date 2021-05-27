FROM registry.access.redhat.com/ubi8/python-38:latest

USER 0

COPY ./requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY ./app /app
WORKDIR /app/

ENV PYTHONPATH=/app

EXPOSE 8080

USER 1001

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]
