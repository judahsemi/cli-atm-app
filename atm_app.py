import os
import time
import random
import math
import json
import functools

import config as cfg
import data_mgt
import utils



class ATMApp():
    def __init__(self):
        """ """
        print("Welcome to {} Bank.".format(cfg.BANK_NAME), flush=True)

        # Intialise database
        self.db = data_mgt.Database(file_dir=cfg.DB_DIR, silent_load=cfg.DB_SILENT_LOAD)
        self.curr_user = None

        # Check if an admin user exist in database, else create one
        if not self.db.admin:
            print("\nAdmin not found. An admin is required to start the app.", flush=True)
            self.create_admin()


    @utils.logout_required
    @utils.delay_run(cfg.DELAY_RUN_SLOW)
    def create_admin(self):
        """ Create a new account and set it to admin and current user. """
        print("\nPlease fill the following fields to create an admin account.", flush=True)

        # Get user input
        name = "Administrator"
        age = random.randint(cfg.ACCT_MIN_AGE, cfg.ACCT_MAX_AGE)
        password = self.convert_prompt("your admin password", str)
        
        # Create user (as admin only but not regular app user)
        user = data_mgt.UserAccount(name, age, password, list(self.db.users.keys()))
        self.db.admin = user
        self.curr_user = user
        
        print("\nAdmin created successfully.", flush=True)
        print("\nYour admin account number {}.".format(user.acct_no), flush=True)
        return self.save_database()


    @utils.admin_required
    @utils.delay_run(cfg.DELAY_RUN_SLOW)
    def admin_menu(self):
        """ Action menu for admin. Requires admin login. """
        print("\n"+"#"*15, "Admin Menu", "#"*15, flush=True)
        print("\nHi {}, what else do you want to do?".format(self.curr_user.name), flush=True)
        
        actions = ["Save database", "Logout", "Exit"]
        option = self.action_prompt(actions)
        if option == 1:
            return self.save_database()

        elif option == 2:
            return self.logout()

        elif option == 3:
            exit()
            
        raise RuntimeError()

    @utils.admin_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def save_database(self):
        """ Saves database as json file. Requires admin login. """
        self.db.save_db(cfg.DB_DIR)
        print("\nRedirecting to the admin menu...", flush=True)


    @utils.logout_required
    @utils.delay_run(cfg.DELAY_RUN_SLOW)
    def guest_menu(self):
        """ Action menu for guest. Requires logout. """
        print("\n"+"#"*15, "Guest Menu", "#"*15, flush=True)
        print("\nWelcome Guest, do you want to register or login to your account?", flush=True)
        
        actions = ["Register", "Login", "Exit"]
        option = self.action_prompt(actions)
        if option == 1:
            return self.register()

        elif option == 2:
            return self.login()

        elif option == 3:
            exit()
            
        raise RuntimeError()

    @utils.logout_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def register(self):
        """ Create a new account and set it to current user. Requires logout. """
        print("\nPlease fill the following fields to create your account.", flush=True)

        # Get user input
        name = self.convert_prompt("your name", str)
        age = self.convert_prompt("your age", int)
        if not (cfg.ACCT_MIN_AGE < age < cfg.ACCT_MAX_AGE):
            msg = "Must be {} - {} years old.".format(cfg.ACCT_MIN_AGE, cfg.ACCT_MAX_AGE)
            raise InterruptedError(msg)
        password = self.convert_prompt("your password", str)
        
        # Create user
        user = data_mgt.UserAccount(name, age, password, list(self.db.users.keys()))
        self.db.add_user(user)
        self.curr_user = user
        
        print("\nRegistration successful.", flush=True)
        return self.display_acct_details()

    @utils.logout_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def login(self):
        """ Login to account and set it to current user. Requires logout. """
        print("\nPlease enter your details to access your account.", flush=True)
        
        # Get user input
        acct_no = self.convert_prompt("your account number", int)
        password = self.convert_prompt("your account password", str)

        # Authenticate login
        user = self.db.get_user(acct_no)
        if not user or user.password != password:
            msg = "Account number or password is incorrect."
            raise InterruptedError(msg)
        self.curr_user = user

        print("\nLogin successful. Redirecting to the right menu...", flush=True)
    

    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_SLOW)
    def user_menu(self):
        """ Action menu for user. Requires login. """
        print("\n"+"#"*15, "Main Menu", "#"*15, flush=True)
        print("\nHi {}, what else do you want to do?".format(self.curr_user.name), flush=True)
        
        actions = ["Check Account Details", "Cash Withdrawal", "Cash deposit",
                   "Cash Transfer", "Contact Us", "Logout", "Exit"]
        option = self.action_prompt(actions)
        if option == 1:
            return self.display_acct_details()

        elif option == 2:
            return self.cash_withdrawal()
        
        elif option == 3:
            return self.cash_deposit()

        elif option == 4:
            return self.cash_transfer()
        
        elif option == 5:
            return self.contact_us()
        
        elif option == 6:
            return self.logout()

        elif option == 7:
            exit()
            
        raise RuntimeError()

    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def display_acct_details(self):
        """ Display current user profile. Requires login. """
        print("\n"+"#"*15, "Account Details", "#"*15, flush=True)
        print("\nHere are your account details.\n".format(self.curr_user.name), flush=True)

        # Display user details
        acct_details = dict(self.curr_user.acct_details()[1:])
        pad = max([len(k) for k in acct_details])
        for name, value in acct_details.items():
            print("{:{}} : {}".format(name, pad, value), flush=True)

        print("\nRedirecting to the main menu...", flush=True)
    
    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def cash_withdrawal(self):
        """ Withdraw cash from current user. Requires login. """
        print("\nFill the following fields to withdraw funds from your account.", flush=True)
        
        # Get user input
        amount = self.convert_prompt("withdraw amount", float)
        if amount <= 0:
            msg = "Must be greater than #0."
            raise InterruptedError(msg)

        if self.curr_user.balance < amount:
            msg = "Insufficient funds."
            raise InterruptedError(msg)
        
        # Update user balance
        self.curr_user.balance -= amount
        self.db.edit_user(self.curr_user)
        
        print("\nTransaction successful. Redirecting to the main menu...", flush=True)

    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def cash_deposit(self):
        """ Deposit cash to current user. Requires login. """
        print("\nFill the following fields to deposit funds to your account.", flush=True)
        
        # Get user input
        amount = self.convert_prompt("deposit amount", float)
        if amount <= 0:
            msg = "Must be greater than #0."
            raise InterruptedError(msg)

        # Update user balance
        self.curr_user.balance += amount
        self.db.edit_user(self.curr_user)
        
        print("\nTransaction successful. Redirecting to the main menu...", flush=True)

    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def cash_transfer(self):
        """ Transfer cash from current user to another user. Requires login. """
        print("\nFill the following fields to transfer funds from your account.", flush=True)
        
        r_acct_no = self.convert_prompt("receiver's account number", int)
        r_user = self.db.get_user(r_acct_no)
        if not r_user or r_user == self.db.admin:
            msg = "Account number does not exist."
            raise InterruptedError(msg)
        
        if self.curr_user == r_user:
            msg = "Same account transfer detected."
            raise InterruptedError(msg)
            
        amount = self.convert_prompt("transfer amount", float)
        if amount <= 0:
            msg = "Must be greater than #0."
            raise InterruptedError(msg)

        if self.curr_user.balance < amount:
            msg = "Insufficient funds."
            raise InterruptedError(msg)
            
        # Update users balance
        self.curr_user.balance -= amount
        self.db.edit_user(self.curr_user)
        r_user.balance += amount
        self.db.edit_user(r_user)
        
        print("\nTransaction successful. Redirecting to the main menu...", flush=True)
    
    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def contact_us(self):
        """ Send message to admin. Requires login. """
        print("\nWhat do you want to tell us?", flush=True)
        
        # Get user input and send it to admin
        msg = self.convert_prompt("your message", str)
        self.db.add_message(self.curr_user, msg)
        
        print("\nThank you for contacting us. Redirecting to main menu...", flush=True)
    
    @utils.login_required
    @utils.delay_run(cfg.DELAY_RUN_NORM)
    def logout(self):
        """ Logout current user. Requires login. """
        self.curr_user = None
        print("\nLog out successful. Redirecting to home menu...", flush=True)

    @staticmethod
    @utils.delay_run(cfg.DELAY_RUN_FAST)
    def action_prompt(actions):
        while True:
            print(flush=True)
            pad = int(math.log(len(actions), 10)) + 1
            for i, act in enumerate(actions, 1):
                print("{:{}}. {}".format(i, pad, act), flush=True)
        
            option = input("\n>>> Select from the above options.\n")
            try:
                option = int(option)
                if 0 < option < len(actions)+1:
                    break
                print("\nInvalid input. Must be from 1 to {}.".format(len(actions)), flush=True)
                    
            except ValueError:
                print("\nInvalid input. Must be a number. Try again.", flush=True)
                
        return option

    @classmethod
    @utils.delay_run(cfg.DELAY_RUN_FAST)
    def convert_prompt(cls, name, func):
        value = func(utils.loop_input_with_check(
            func,
            "\n>>> Enter {}. (Type {} to cancel)\n".format(name, cfg.CANCEL_ACTION),
            "\nInvalid input. Must be of type {}. Try again.".format(func.__name__),
            ValueError))
        return value

