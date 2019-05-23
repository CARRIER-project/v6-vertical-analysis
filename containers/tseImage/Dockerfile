FROM datasharing/base

COPY run.py run.py
COPY run.r run.r
COPY run.sh run.sh

RUN dos2unix /run.py
RUN dos2unix /run.r
RUN dos2unix /run.sh

CMD ["sh", "run.sh"]