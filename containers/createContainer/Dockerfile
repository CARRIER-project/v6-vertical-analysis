FROM r-base:latest

COPY prepare.r prepare.r
COPY run.r run.r

RUN Rscript prepare.r

CMD ["Rscript", "run.r"]