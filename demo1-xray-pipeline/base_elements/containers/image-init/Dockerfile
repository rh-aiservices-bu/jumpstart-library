FROM registry.access.redhat.com/ubi8/python-39:1-24

WORKDIR /usr/src/app

COPY requirements.txt image-init.py ./

RUN pip install -r requirements.txt

USER 1001

COPY --chown=1001:0 base_images/. /opt/app-root/src/xray-data/

CMD ["python", "-u", "image-init.py"]
