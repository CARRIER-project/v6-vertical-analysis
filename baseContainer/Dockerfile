FROM python:3.6.9-slim-stretch

RUN apt-get update && apt-get install -y python-pip

RUN mkdir /data

RUN mkdir /models

RUN mkdir /inputVolume

RUN mkdir /output

COPY pp_enc.py pp_enc.py

COPY run.py run.py

RUN pip install \
  'mock==3.0.5' \
  'pynacl==1.3.0' \
  'crypto==1.4.1' \
  'pycrypto==2.6.1' \
  'pandas==0.25.1' \
  'numpy==1.17.2' \
  'scikit-learn==0.21.3' \
  'SPARQLWrapper==1.8.4' \
  'requests==2.22.0' \
  'seaborn==0.9.0' \
  'bokeh==1.3.4' \
  'pyreadstat==0.2.9'\
  'scipy==1.4.1' \
  'PyYAML==5.3'

ADD PQcrypto/PQencryption/ /usr/local/lib/python3.6/site-packages/PQencryption/
ADD redacted_logging /usr/local/lib/python3.6/site-packages/redacted_logging/
ADD config.ini /

CMD ["python", "run.py"]
