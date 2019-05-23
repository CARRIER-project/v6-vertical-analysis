FROM datasharing/base

COPY prepare.r /prepare.r
COPY encrypt.py /encrypt.py
COPY run.sh /run.sh

RUN dos2unix prepare.r
RUN dos2unix encrypt.py
RUN dos2unix run.sh

CMD ["sh", "/run.sh"]