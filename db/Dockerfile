FROM postgres:15

WORKDIR /docker-entrypoint-initdb.d

COPY init_db.sh /docker-entrypoint-initdb.d/
COPY data.csv /docker-entrypoint-initdb.d/

RUN chmod +x /docker-entrypoint-initdb.d/init_db.sh
