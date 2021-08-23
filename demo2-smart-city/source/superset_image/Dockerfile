FROM quay.io/internaldatahub/superset:1.1.0
USER root
COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
USER superset
