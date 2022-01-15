FROM registry.access.redhat.com/ubi8/python-39:1-24

WORKDIR /usr/src/app

COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "-u", "image-generator.py"]
