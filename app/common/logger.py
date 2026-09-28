# import os
# import logging
# from datetime import datetime

# LOGS_DIR='logs_data'
# os.makedirs(LOGS_DIR,exist_ok=True)

# LOGS_FILE=os.path.join(
#     LOGS_DIR,
#     f'log_{datetime.now().strftime('%Y-%m-%d')}.log')

# logging.basicConfig(
#     filename=LOGS_FILE,
#     format='%(asctime)s -%(levelname)s -%(message)s',
#     level=logging.INFO,
#  )

# def get_logger(name):
#     logger=logging.getLogger(name)
#     logger.setLevel(logging.INFO)
#     return logger

import logging
import os
from datetime import datetime

# Create logs folder if not exists
os.makedirs("logs", exist_ok=True)

LOGS_FILE = os.path.join(
    "logs",
    f"bulkmate_{datetime.now().strftime('%Y-%m-%d')}.log"
)
# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    filename=LOGS_FILE,
    # handlers=[
    #     logging.FileHandler(f"logs/bulkmate.log"),  # saves to file
    #     #logging.StreamHandler()                      # also prints to terminal
    # ]
)

logger = logging.getLogger("BulkMate")