import os
import time
import random
import math
import json
import functools

import config as cfg



def check_user_exists(exists_ok):
    def check_exists(func):
        @functools.wraps(func)
        def run(db, user, *args, **kwargs):
            if (user.id in db.users) == exists_ok:
                return func(db, user, *args, **kwargs)

            if exists_ok:
                raise Exception("User not found. Request denied.")
            raise Exception("User already exists. Request denied.")
        return run
    return check_exists

def admin_required(func):
    @functools.wraps(func)
    def run(self, *args, **kwargs):
        if self.curr_user and self.curr_user == self.db.admin:
            return func(self, *args, **kwargs)
        else:
            print("\nYou need to be logged in as admin to do this.", flush=True)
    return run

def login_required(func):
    @functools.wraps(func)
    def run(self, *args, **kwargs):
        if self.curr_user:
            return func(self, *args, **kwargs)
        else:
            print("\nYou need to be logged in to do this.", flush=True)
    return run

def logout_required(func):
    @functools.wraps(func)
    def run(self, *args, **kwargs):
        if not self.curr_user:
            return func(self, *args, **kwargs)
        else:
            print("\nYou need to be logged out to do this.", flush=True)
    return run

def delay_run(sec):
    def delay(func):
        @functools.wraps(func)
        def run(*args, **kwargs):
            time.sleep(sec)
            return func(*args, **kwargs)
        return run
    return delay

def loop_input_with_check(validation, input_msg=None, error_msg=None, exception=None):
    input_msg = "\n>>> Enter\n" if input_msg is None else input_msg
    error_msg = "\nInvalid field." if error_msg is None else error_msg
    exception = Exception if exception is None else exception

    while True:
        value = input(input_msg)
        if value == cfg.CANCEL_ACTION:
            raise InterruptedError("Cancelling request.")

        try:
            value = validation(value)
            break

        except exception:
            print(error_msg, flush=True)

        except:
            raise Exception
    return value

