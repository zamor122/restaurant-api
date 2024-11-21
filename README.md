# restaurant-api
## Steps to run
  - Clone the repo
  - `CD` into your projects root directory
  - Create a `.env` file in the format listed below in your project root dir
  - Run `docker compose up --build` 
    -- This command runs and loads the data into the DB
    -- It also runs a normalization script to cleanse and store the data in two separate tables
      1. A table holding all data from the restaurants.csv file that matches the original schema
      2. A table that has the cleansed usable version of the data that we use in the API calls
  - [Head the the API](http://localhost)
  - Visit the restaurants endpoint:       
    - http://localhost/restaurants/search
      - this page provides all open restaurant names with the current local time (timezone not considered)
    - http://localhost/restaurants/[datetimestr] 
      - (ex. 2024-11-21T12:30:00)
      - uses ISO format to take in a string directly in the path and return all open restaurant names

## Stack
- Docker compose 
- Flask (lightweight python API frameowrk)
  - Running on a production level nginx proxy server
  - Gunicorn server running under nginx to handle some weight of traffic for Flask
- PostgresSQL

## Future Improvements
- Asyncronous data intake via supervisor or better AWS Lambda
- Better cleaning/normalizing of data, more dynamic and robust to handle different schemas
- Pagination for API use
- Authorization
- Implement Terraform to deploy out to EC2/AWS services
- File structure
- Async queue for handling large file processing (celery, beet, etc,.)

## Q&A
- Why no Django?
  - I felt Django was too dense for this application. As the scope is just an API, Django carries a lot of extra weight (like an ORM, admin panel, and built-in authentication). Flask (with Gunicorn and Nginx) is the ideal candidate for this solution. It provides quick implementation of the api and easy legibility of code
- No ORM?
  - While I was going to implement Flask-SQLAlchemy initially, using an ORM would have complicated things. I wanted the code to be simple and easy to read. An ORM would be better for larger apps.

- Why Flask?
  - Flask is a lightweight python API framework designed specifically for services like this. I thought this was a great use case to show off Flask and it's simplicity. It's quick but not dirty and with the right design, it can scale well for services like this.

- How does the data get loaded from `restaurants.csv`?
  - Upon running `docker compose up --build`, the db container comes up first. This allows the entrypoint files (in db directory) to be transferred over into the entrypoint container to be ran. We upload the original file to a table (after creating it) and work with that data from there on. This DB creation and loading only happens the first time the docker container is built and will skip initialization unless the volumes are deleted.
  
  - After that's done, we start our Nginx container and then our Flask app, where we transfer the script `normalize_data.py` which allows us to normalize the data, parse it, cleanse it and enter it into a new table: `restaurant_hours`. This will run each time the flask app starts up which is why we don't restart it. It also deletes `restaurant_hours` and creates the table each time the container is built as well, checking for changes in the main `restaurants` table.

- Why didn't I cleanse the data asynchronously or with a different service? Isn't that bad?
  - In production I would use something like an upload file data pipeline where along the way we cleanse and normalize the file line by line in a queue so we make sure to get all the data right and can try again if we need to.
  
  - I didn't implement asynchronous data processing because I felt like it was out of the scope for this project and since the data won't change much then it's fine. 





### .env File (for local)
```
FLASK_APP=app.py
FLASK_ENV=development
FLASK_APP=app.py
FLASK_ENV=development
DB_HOST=db
DB_USER=postgres
DB_PASSWORD=password
DB_NAME=restaurant_db
DB_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=restaurant_db
SECRET_KEY=supersecretkey
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost:5432/restaurant_db
```
