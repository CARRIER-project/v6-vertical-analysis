FROM python:2-stretch

RUN apt-get update && apt-get install -y r-base r-base-dev python-pip

RUN mkdir /data

COPY prepare.sh prepare.sh
COPY run.py run.py

RUN sh prepare.sh

CMD ["python", "run.py"]