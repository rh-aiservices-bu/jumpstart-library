FROM registry.access.redhat.com/ubi8/python-39:1-24

WORKDIR /usr/src/app

COPY requirements.txt risk-assessment.py pneumonia_model.h5 FreeMono.ttf ./

RUN pip install -r requirements.txt

CMD ["python", "-u", "risk-assessment.py"]
