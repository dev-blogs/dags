FROM ubuntu:16.04

RUN mkdir -p /usr/src/dags
RUN mkdir -p /usr/src/scripts

WORKDIR /usr/src

COPY dags/* /usr/src/dags/
COPY scripts/* /usr/src/scripts/

CMD ["sh", "entrypoint.sh"]
