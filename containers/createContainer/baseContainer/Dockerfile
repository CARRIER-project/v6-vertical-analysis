FROM python:2-stretch

RUN apt-get update && apt-get install -y r-base r-base-dev python-pip dos2unix

RUN mkdir /data

COPY run.py run.py

RUN pip install mock pynacl crypto pycrypto

ADD PQcrypto/PQencryption/ /usr/local/lib/python2.7/site-packages/PQencryption/

CMD ["python", "run.py"]