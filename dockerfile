FROM mysql:latest
COPY ./my.sql /docker-entrypoint-initdb.d/

