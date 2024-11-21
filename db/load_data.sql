COPY restaurants(name, hours)
FROM '/docker-entrypoint-initdb.d/restaurants.csv'
DELIMITER ','
CSV HEADER;
