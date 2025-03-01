FROM devblogs1/ubuntu-image-with-rsync:1.0

RUN mkdir -p /usr/src/dags
RUN mkdir -p /usr/src/scripts

WORKDIR /usr/src

COPY dags/* /usr/src/dags/
COPY scripts/* /usr/src/scripts/

RUN chmod 777 /usr/src/dags/*

CMD ["sh", "scripts/entrypoint.sh"]
