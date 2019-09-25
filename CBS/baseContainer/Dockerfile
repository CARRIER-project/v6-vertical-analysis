FROM python:3.6.9-slim-stretch

RUN apt-get update && apt-get install -y python-pip

RUN mkdir /data

RUN mkdir /encryption

RUN mkdir /output

COPY run.py run.py

RUN pip install --no-cache-dir \
  'pynacl==1.3.0' \
  'crypto==1.4.1' \
  'pycrypto==2.6.1' \
  'pandas==0.25.1' \
  'numpy==1.17.2' \
  'scikit-learn==0.21.3' \
  'seaborn==0.9.0' \
  'bokeh==1.3.4' \
  'pyreadstat==0.2.9' \
  'SPARQLWrapper==1.8.4' \
  'requests==2.22.0'

ADD PQcrypto/PQencryption/ /usr/local/lib/python3.6/site-packages/PQencryption/

CMD ["python", "run.py"]
