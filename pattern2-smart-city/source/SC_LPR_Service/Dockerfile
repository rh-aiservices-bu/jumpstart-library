FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
COPY ./requirement.txt requirement.txt
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install -r requirement.txt
COPY ./app /app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
