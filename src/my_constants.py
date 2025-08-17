# src/my_constants.py
from os import path
TABLE_IGNORE_PHONE_NUMBER = "TABLE_IGNORE_PHONE_NUMBER"
TABLE_IGNORE_UID = "TABLE_IGNORE_UID"
TABLE_RESULTS = "TABLE_RESULTS"

DATA_TABLES = {
    "Ignore phone": TABLE_IGNORE_PHONE_NUMBER,
    "Ignore uid": TABLE_IGNORE_UID,
    "Results": TABLE_RESULTS,
}

DB_CONNECTION = "DB_CONNECTION"
DB_CONTAINER_PATH = path.abspath("./repositories/db")

SCRAPING = "scraping"
LAUNCHING = "launching"
