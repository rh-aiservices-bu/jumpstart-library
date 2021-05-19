FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY ./requirements.txt requirements.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirements.txt
COPY ./app /app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
