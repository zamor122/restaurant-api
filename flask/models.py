import psycopg2
import os
import logging
from dotenv import load_dotenv
from datetime import datetime
from constants import RESTAURANT_HOURS_TABLE_NAME, RESTAURANTS_TABLE_NAME

load_dotenv()

class Database:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = os.getenv('DB_PORT')

    def _get_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            logging.info("Database connection established.")
            return conn
        except psycopg2.Error as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def _clear(self, table_name):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
            conn.commit()
            logging.info(f"Successfully truncated table: {table_name}")
            return True
        except Exception as e:
            logging.error(f"Error clearing table {table_name}: {e}")
            conn.rollback()
        finally:
            conn.close()
        return False

    def _check_table_exists(self, table_name):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM   pg_catalog.pg_tables
                    WHERE  schemaname = 'public'
                    AND    tablename = %s
                );
            """, (table_name,))
            result = cursor.fetchone()[0]
            logging.info(f"Table {table_name} exists: {result}")
            return result
        except Exception as e:
            logging.error(f"Error checking if table {table_name} exists: {e}")
            raise
        finally:
            conn.close()

class RestaurantsModel:
    def __init__(self, db: Database):
        self.db = db

    def fetch_all_restaurants(self):
        conn = self.db._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id, hours FROM {RESTAURANTS_TABLE_NAME}")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error fetching restaurants: {e}")
            raise
        finally:
            conn.close()

class RestaurantHoursModel:
    def __init__(self, db: Database):
        self.db = db

    def _save_to_database(self, data_list):
        conn = self.db._get_connection()
        try:
            cursor = conn.cursor()
            for restaurant_hours in data_list:
                cursor.execute(
                    """
                    INSERT INTO restaurant_hours (restaurant_id, day, opening_time, closing_time)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        restaurant_hours['restaurant_id'],
                        restaurant_hours['day'],
                        restaurant_hours['open_time'],
                        restaurant_hours['close_time']
                    )
                )
            conn.commit()
            logging.info("Data saved to the database successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error saving data to the database: {e}")
            raise
        finally:
            conn.close()

    def _clear(self):
        return self.db._clear(table_name=RESTAURANT_HOURS_TABLE_NAME)

    def _check_exists(self):
        return self.db._check_table_exists(table_name=RESTAURANT_HOURS_TABLE_NAME)
    
    # return restaurants open according to string, if no string, return all open now (with current local time for simplicity)
    def _get_open_restaurants(self, day_of_week: str, time: str) -> list[str]:
        try:
            conn = self.db._get_connection()
            cursor = conn.cursor()

            query = """
            WITH hour_match AS (
                SELECT rh.restaurant_id, rh.day, rh.opening_time, rh.closing_time
                FROM restaurant_hours rh
                WHERE rh.day = %s
                  AND (
                    (%s >= rh.opening_time AND %s < rh.closing_time)
                    OR
                    (rh.opening_time > rh.closing_time 
                      AND (%s >= rh.opening_time OR %s < rh.closing_time))
                  )
            )
            SELECT r.name
            FROM restaurants r
            INNER JOIN hour_match hm ON r.id = hm.restaurant_id;
            """

            cursor.execute(query, (day_of_week, time, time, time, time))
            results = cursor.fetchall()

            restaurant_names = [row[0] for row in results]
            return restaurant_names
        except Exception as e:
            logging.error(f"Error fetching data from restaurant_hours: {e}")
            raise
        finally:
            if conn:
                conn.close()
