import imp
import os
import sys

'''
import json
from users import users_repository
from users import User

RES_DB = "serverfiles/residents.json"

with open(RES_DB, 'r') as f:
    str_content = f.read()
    json_obj = json.loads(str_content)
    residents = json_obj['residents']
    for resident in residents:
        user = User(
            users_repository.next_index(),
            resident['unit'],
            resident['userid'],
            resident['password'],
            resident['name'],
            resident['email'],
            resident['startdt'],
            resident['phone'],
            resident['type'],
            resident['ownername'],

            resident['owneremail'],
            resident['ownerphone'],
            resident['owneraddress'],
            resident['isrental'],
            resident['emerg_name'],
            resident['emerg_email'],
            resident['emerg_phone'],
            resident['emerg_has_key'],
            resident['occupants'],
            resident['oxygen_equipment'],

            resident['limited_mobility'],
            resident['routine_visits'],
            resident['has_pet'],
            resident['bike_count'],
            resident['insurance_carrier'],
            resident['valve_type'],
            resident['no_vehicles'],
            resident['vehicles'],
            resident['last_update_date'],
            resident['notes']
        )
        users_repository.add_user_to_dict(user)
'''

'''
print("Here is one user:")
user = users_repository.get_user_by_unit(26)
print(user.get_json_data())
'''

# loads a file named 'server.py'
sys.path.insert(0, os.path.dirname(__file__))
wsgi = imp.load_source('wsgi', 'server.py')

# the Flask object in server.py must be assigned to a variable named 'app'
application = wsgi.app
