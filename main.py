import os
import time
import random
import math
import json
import functools

import config as cfg
import atm_app
import data_mgt
import utils



if __name__ == "__main__":
    # Start app
    try:
        app = atm_app.ATMApp()

    except InterruptedError:
        print("\nYou stopped the Application from starting. Goodbye...", flush=True)
        exit()

    except:# Exception as msg:
        # print(msg)
        print("\nApplication failed to start. Goodbye...", flush=True)
        exit()
    
    # Run app
    while True:
        try:
            if app.curr_user == app.db.admin:
                app.admin_menu()

            elif app.curr_user:
                app.user_menu()
                    
            else:
                app.guest_menu()
            
        except InterruptedError as msg:
            print("\n{} Request denied.".format(msg), flush=True)
            continue

        except:
            try:
                app.db.save_db(cfg.DB_DIR)

            except:
                print("\nDatabase failed to save during emergency shutdown...", flush=True)
            print("\nApplication stopped. Shutting down app...", flush=True)
            exit()

