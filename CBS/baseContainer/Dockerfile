FROM python:3.6-slim-stretch

RUN apt-get update && apt-get install -y python-pip

RUN mkdir /data

RUN mkdir /encryption

RUN mkdir /output

COPY run.py run.py

RUN pip install pynacl crypto pycrypto pandas numpy sklearn seaborn bokeh pyreadstat SPARQLWrapper requests

ADD PQcrypto/PQencryption/ /usr/local/lib/python3.6/site-packages/PQencryption/

CMD ["python", "run.py"]
