import os
import time
import random
import math
import json
import functools



# DATABASE
DB_DIR = "./"
DB_SILENT_LOAD = True

# User CLASS
ACCT_NO_PREFIX = 200
ACCT_NO_BASE_LENGTH = 8

USER_EDIT_FIELDS = ["name", "balance", "password"]

# APP
BANK_NAME = "ZURI"
CANCEL_ACTION = "CANCEL"

ACCT_MIN_AGE = 12
ACCT_MAX_AGE = 120

DELAY_RUN_FAST = 0.8
DELAY_RUN_NORM = 1.5
DELAY_RUN_SLOW = 2.2

