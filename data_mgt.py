import os
import time
import random
import math
import json
import functools

import config as cfg
import utils



class Database():
    """
    """
    def __init__(self, *, file_dir=None, silent_load=True):
        """
        """
        self.admin = None
        self.users = {}
        self.messages = {}

        if file_dir:
            self.load_db(file_dir, silent_load)
        
    def get_user(self, _id):
        if str(_id) == self.admin.id:
            return self.admin
        return self.users.get(str(_id), None)

    @utils.check_user_exists(exists_ok=False)
    def add_user(self, user):
        self.users[user.id] = user
        return self.users[user.id]

    @utils.check_user_exists(exists_ok=True)
    def edit_user(self, user):
        self.users[user.id] = user
        return self.users[user.id]

    @utils.check_user_exists(exists_ok=True)
    def delete_user(self, user):
        return self.users.remove(user)

    @utils.check_user_exists(exists_ok=True)
    def add_message(self, user, msg):
        if user.id in self.messages:
            self.messages[user.id].append(msg)
        else:
            self.messages[user.id] = [msg]

    def save_db(self, file_dir):
        admin = {self.admin.id: dict(self.admin.acct_details())}
        users = {_id: dict(u.acct_details()) for _id, u in self.users.items()}
        data = {"admin": admin, "users": users, "messages": self.messages}

        file_path = os.path.join(file_dir, "db.json")
        with open(file_path, "w") as db_file:
            json.dump(data, db_file, indent=4)

        print("\nDatabase saved successfully at '{}'.".format(file_path), flush=True)

    def load_db(self, file_dir, silent_load=True):
        try:
            file_path = os.path.join(file_dir, "db.json")
            with open(file_path, "r") as db_file:
                data = json.load(db_file)

            self.admin = UserAccount.from_dict(list(data["admin"].values())[0])
            self.users = {_id: UserAccount.from_dict(u_dict) for _id, u_dict in data["users"].items()}
            self.messages = data["messages"]
        except:
            print("\nAn error occured while loading database from file.", flush=True)
            if not silent_load:
                raise Exception()
            print("\nIgnoring all errors...", flush=True)
            return None
        print("\nDatabase loaded successfully from '{}'.".format(file_path), flush=True)



class UserAccount:
    def __init__(self, name, age, password, exclude_list):
        """
        """
        acct_no = self.generate_acct_no(exclude_list)
        
        self._id = str(acct_no)
        self.name = name
        self._age = age
        self._acct_no = acct_no
        self.balance = 0.0
        self.password = password

    @property
    def id(self):
        return self._id

    @property
    def age(self):
        return self._age

    @property
    def acct_no(self):
        return self._acct_no
        
    @staticmethod
    def generate_acct_no(exclude_list):
        min_range = 10 ** cfg.ACCT_NO_BASE_LENGTH
        max_range = (min_range * 10) - 1
        
        acct_no = int(f"{cfg.ACCT_NO_PREFIX}{random.randint(min_range, max_range)}")
        while acct_no in exclude_list:
            acct_no = int(f"{cfg.ACCT_NO_PREFIX}{random.randint(min_range, max_range)}")
        return acct_no
    
    def edit_user(self, **kwargs):
        for k, v in kwargs.items():
            if k in cfg.USER_EDIT_FIELDS and isinstance(v, type(getattr(self, k))):
                setattr(self, k, v)
        return self

    def acct_details(self):
        return [
            ("ID", self.id),
            ("Name", self.name),
            ("Age", self.age),
            ("Account Number", self.acct_no),
            ("Account Balance", self.balance),
            ("Password", self.password)]

    @classmethod
    def from_dict(cls, u_dict):
        init_kwargs = {
            "name": u_dict["Name"],
            "age": u_dict["Age"],
            "password": u_dict["Password"]}
        user = cls(**init_kwargs, exclude_list={})
        user._id = u_dict["ID"]
        user._acct_no = u_dict["Account Number"]
        user.balance = u_dict["Account Balance"]
        return user
        
    def __eq__(self, other):
        if not isinstance(other, UserAccount):
            return False
        return self.id == other.id
        
    def __repr__(self):
        return "<User: {} {}>".format(self.acct_no, self.name)

