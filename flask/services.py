import re
from datetime import datetime
import logging
from models import Database, RestaurantsModel, RestaurantHoursModel
from helpers import convert_to_time

class NormalizeData:
  def __init__(self):
    db = Database()
    self.restaurant_model = RestaurantsModel(db)
    self.restaurant_hours_model = RestaurantHoursModel(db)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


  def expand_day_range(self, day_range):
    day_mapping = {
        "Mon": "Monday",
        "Tues": "Tuesday",
        "Wed": "Wednesday",
        "Thu": "Thursday",
        "Fri": "Friday",
        "Sat": "Saturday",
        "Sun": "Sunday"
    }
    ordered_days = ["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]

    parts = day_range.split(',')

    expanded_days = []

    for part in parts:
        part = part.strip()

        #check if date range
        if '-' in part:
            start_day, end_day = map(str.strip, part.split('-'))
            
            start_index = ordered_days.index(start_day)
            end_index = ordered_days.index(end_day)
            
            expanded_days.extend(ordered_days[start_index:end_index + 1])
        else:
           #single day
            expanded_days.append(part)

    #get full names
    return [day_mapping[day] for day in expanded_days]

  def cleanse_and_normalize_data(self):
    cleaned_data = []

    #regex to match time
    time_pattern = re.compile(r'(\d{1,2}(:\d{2})?\s?(am|pm)\s?-\s?\d{1,2}(:\d{2})?\s?(am|pm))')

    try:
        restaurants = self.restaurant_model.fetch_all_restaurants()
        for restaurant_id, hours in restaurants:
            hours_segments = hours.split('/')
            
            for segment in hours_segments:
              segment = segment.strip()
        
              time_match = time_pattern.search(segment)
              if time_match:
                  times_part = time_match.group(0).strip()
                  days_part = segment[:time_match.start()].strip()
                  
                  day_ranges = [day.strip() for day in days_part.split(',')]
                  
                  open_time, close_time = map(str.strip, times_part.split('-'))
                  
                  for day_range in day_ranges:
                    for day in self.expand_day_range(day_range):
                      opening_time = convert_to_time(open_time)
                      closing_time = convert_to_time(close_time)
                      
                      cleaned_data.append({
                        'restaurant_id': restaurant_id,
                        'day': day,
                        'open_time': opening_time,
                        'close_time': closing_time
                      })

        return cleaned_data
    except Exception as e:
        logging.error("Error during data cleansing: %s", e)
        raise

  def normlize_data_service(self):
    try:
      if self.restaurant_hours_model._check_exists():
        if self.restaurant_hours_model._clear():
          normalized_data = self.cleanse_and_normalize_data()
          if normalized_data:
            logging.info("Data normalized successfully")
            self.restaurant_hours_model._save_to_database(normalized_data)
            return True
          else:
            logging.error("Data normalization failed")
        else: 
          logging.error("Soemthing else")
      return False
    except Exception as e:
      logging.error("Error during normalization service: %s", e)
      raise

class RestaurantHours:
    def __init__(self):
      db = Database()
      self.restaurant_hours = RestaurantHoursModel(db)
      logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_open_restaurants(self, datetime_str: str = ""):
        # If no datetime_str is provided, use current datetime
        if not datetime_str:
            now = datetime.now()
            datetime_str = now.isoformat()

        # Parse the datetime string and extract the day and time
        try:
            date_obj = datetime.fromisoformat(datetime_str)
        except ValueError:
            logging.error("Invalid datetime format. Please use 'YYYY-MM-DDTHH:MM:SS' (ISO format).")
            return {
               "status": "failure",
               "status_code": 400,
               "message": "Invalid datetime format. Please use 'YYYY-MM-DDTHH:MM:SS (ISO format)"
            }

        day_of_week = date_obj.strftime('%A')  # Get the full day name (e.g., "Monday")
        time = date_obj.time() 

        # Call the model to fetch open restaurants
        try:
            open_restaurants = self.restaurant_hours._get_open_restaurants(day_of_week, time)
            return {
                "status": "success", 
                "status_code": 200, 
                "data": open_restaurants
            }
        except Exception as e:
            logging.error(f"Error while fetching open restaurants: {e}")
            return {"status": "failure", "status_code": 500, "message": "Internal server error."}