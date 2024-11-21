import re
from datetime import datetime
import logging
from services import NormalizeData

has_run = False

normalize_data_service = NormalizeData()

if __name__ == "__main__":
    if not has_run:
        try:
          normalize_data_service.normlize_data_service()
        except Exception as e:
          logging.error("Error running main logic: %s", e)
        has_run = True
