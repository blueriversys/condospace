"""
   Defines classses and variables related to the handling of users.
"""

import os
import json
from flask_login import UserMixin
from werkzeug.utils import secure_filename

USER_TYPE_ADMIN = 0
USER_TYPE_BOARD = 1
USER_TYPE_SECRETARY = 2
USER_TYPE_RESIDENT = 3


class User(UserMixin):
    def __init__(self, unit, userid, username, password, headname, heademail, headphone, ownername, owneremail, ownerphone, occupants, id, startdt, type, active=True):
        self.unit = unit
        self.userid = userid
        self.username = username
        self.password = password
        self.headname = headname
        self.heademail = heademail
        self.headphone = headphone
        self.ownername = ownername
        self.owneremail = owneremail
        self.ownerphone = ownerphone
        self.occupants = occupants
        self.id = id
        self.startdt = startdt
        self.type = type
        self.active = active

    def get_unit(self):
        return self.unit

    def get_userid(self):
        return self.userid

    def get_username(self):
        return self.username

    def get_password(self):
        return self.password

    def get_headname(self):
        return self.headname

    def get_heademail(self):
        return self.heademail

    def get_headphone(self):
        return self.headphone

    def get_ownername(self):
        return self.ownername

    def get_owneremail(self):
        return self.owneremail

    def get_ownerphone(self):
        return self.ownerphone

    def get_occupants(self):
        return self.occupants

    def get_id(self):
        return self.id

    def get_startdt(self):
        return self.startdt

    def get_type(self):
        return self.type

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.username , key='secret_key')

class UsersRepository:
    def __init__(self):
        self.unit_dict = dict()
        self.identifier = 0
    
    def save_user(self, user):
        print('here in save_user()')
        print(f'unit {user.unit}, {user.userid}, {user.username},  owner {user.ownername}, {user.owneremail}, {user.ownerphone}')
        self.unit_dict.setdefault(user.unit, user)

    def add_user_to_dict(self, user):
        self.unit_dict.setdefault(user.unit, user)

    def get_user(self, username):
        for key in self.get_users():
            user = self.get_user_by_unit(key)
            if user.username == username:
                return user
        return None
    
    def get_user_by_id(self, userid):
        for key in self.get_users():
            user = self.get_user_by_unit(key)
            if user.id == userid:
                return user
        return None
    
    def get_user_by_unit(self, unit):
        return self.unit_dict.get(unit)
    
    def get_users(self):
        return self.unit_dict
    
    def delete_user(self, user):
        userObj = self.unit_dict.get(user.unit)
        if userObj == None:
            return
        del self.unit_dict[user.unit]

    def next_index(self):
        self.identifier += 1
        return self.identifier

    def save_users_to_file(self, filename):
        print('here in save_users_to_file')
        with open(filename, 'w') as f:
            userslist = []
            for user in self.unit_dict.values():
                record = {
                    'unit': user.unit,
                    'userid': user.userid,
                    'username': user.username,
                    'password': user.password,
                    'headname': user.headname,
                    'heademail': user.heademail,
                    'headphone': user.headphone,
                    'ownername': user.ownername,
                    'owneremail': user.owneremail,
                    'ownerphone': user.ownerphone,
                    'occupants': user.occupants,
                    'startdt': user.startdt,
                    'type': user.type
                }
                userslist.append(record)
            residents = {'residents': userslist}
            json_obj = json.dumps(residents)
            f.write(json_obj)


# define user repository
users_repository = UsersRepository()

# create a few users of different types
#user_admin = User('admin', 'admin@7394', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_ADMIN)

# board members
'''
user_jsilva = User('jsilva', 'joe@7394', 'info@whitegatecondo.com', users_repository.next_index(), USER_TYPE_BOARD)
user_dakins = User('dakins', 'dan@3443', 'nadsnika@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_cbusa = User('cbusa', 'chris@7575', 'mufflermannh@yahoo.com', users_repository.next_index(), USER_TYPE_BOARD)
user_wmann = User('wmann', 'wayne@1348', 'rookiemann57@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_mjohnson = User('mjohnson', 'mary@8765', 'mjculady@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
'''

# authorized secretaries and treasurer
'''
user_vbarrett = User('vbarrett', 'virginia@6465', 'ginnybarrett@comcast.net', users_repository.next_index(), USER_TYPE_SECRETARY)
user_dgilligan = User('dgilligan', 'donna@1331', 'dgilligan89@comcast.net', users_repository.next_index(), USER_TYPE_SECRETARY)
'''

# regular residents
# user_jresident = User('jresident', 'johnpass', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_RESIDENT)


#temporary email addresses
# create a few users of different types
'''
user_admin = User('admin', 'admin@7394', 'info@whitegatecondo.com', users_repository.next_index(), USER_TYPE_ADMIN)
user_jsilva = User('jsilva', 'joe@7394', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_dakins = User('dakins', 'dan@3443', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_cbusa = User('cbusa', 'chris@7575', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_wmann = User('wmann', 'wayne@1348', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_mjohnson = User('mjohnson', 'mary@8765', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_BOARD)
user_vbarrett = User('vbarrett', 'virginia@6465', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_SECRETARY)
user_dgilligan = User('dgilligan', 'donna@1331', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_SECRETARY)
user_jresident = User('jresident', 'johnpass', 'joesilva01862@gmail.com', users_repository.next_index(), USER_TYPE_RESIDENT)
'''


# add users to repository
'''
users_repository.save_user(user_admin)
users_repository.save_user(user_jsilva)
users_repository.save_user(user_dakins)
users_repository.save_user(user_cbusa)
users_repository.save_user(user_wmann)
users_repository.save_user(user_mjohnson)
users_repository.save_user(user_vbarrett)
users_repository.save_user(user_dgilligan)
users_repository.save_user(user_jresident)
'''

