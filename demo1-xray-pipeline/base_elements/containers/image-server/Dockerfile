FROM python:3.7

WORKDIR /usr/src/app

COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "-u", "image-server.py"]
