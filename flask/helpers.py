from datetime import datetime
def convert_to_time(time_string):
    time_obj = datetime.strptime(time_string, "%I:%M %p" if ":" in time_string else "%I %p").time()
    return time_obj