"""
   Defines classes and variables related to the handling of users.
"""

import os
import json
from flask_login import UserMixin
from werkzeug.utils import secure_filename

SEPARATOR_CHAR = "@"

class User(UserMixin):
    def __init__(self, id, userid, password, name, email, active=True):
        self.id = id
        self.userid = userid
        self.password = password
        self.name = name
        self.email = email
        self.active = active

    def get_id(self):
        return self.id

    def get_userid(self):
        return self.userid

    def get_password(self):
        return self.password

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def is_active(self):
        return self.active

    def get_auth_token(self):
        return make_secure_token(self.userid , key='secret_key')


class UsersRepository:
    def __init__(self, aws):
#        self.user_dict = dict() # the key is user_id
        self.tenant_dict = dict()
        self.aws = aws

    def save_user(self, tenant_id, user):
        if not self.tenant_dict[tenant_id]:
            self.tenant_dict[tenant_id] = {  "users": dict() }
        self.tenant_dict[tenant_id]['users'][user.userid] = user

    def reset_tenant_user_dict(self, tenant_id):
        self.tenant_dict[tenant_id] = dict()

    def remove_tenant(self, tenant_id):
        if self.tenant_dict[tenant_id]:
            del self.tenant_dict[tenant_id]

    def get_user_count_by_tenant(self, tenant_id):
        if self.tenant_dict[tenant_id]:
            return len(self.tenant_dict[tenant_id]['users'])

    def get_user_count_total(self):
        count = 0
        for tenant in self.tenant_dict:
            count += self.get_user_count_by_tenant(tenant)
        return count

    def is_tenant_loaded(self, tenant_id):
        if tenant_id in self.tenant_dict:
            return True
        return False

    def get_user_by_userid(self, tenant_id, userid):
        if userid in self.tenant_dict[tenant_id]:
            return self.tenant_dict[tenant_id]['users'][userid]
        # search regardless of casing
        for key, value in self.tenant_dict[tenant_id]['users'].items():
            if key.lower() == userid.lower():
                return value
        return None

    def get_user_by_id(self, tenant_id, id):
        for user in self.get_users(tenant_id):
            if user.id == id:
                return user
        return None

    def get_users(self, tenant_id):
        return self.tenant_dict[tenant_id]['users'].values()

    def delete_user(self, tenant_id, user):
        user_obj = self.tenant_dict[tenant_id]['users'][user.userid]
        if user_obj is None:
            print(f"user not found for {tenant_id} {user.userid}")
            return False
        del self.tenant_dict[tenant_id]['users'][user.userid]
        return True

    def delete_user_by_userid(self, tenant_id, userid):
        user_obj = self.tenant_dict[tenant_id]['users'][userid]
        if user_obj is None:
            print(f"user not found for {tenant_id} {userid}")
            return False
        del self.tenant_dict[tenant_id]['users'][userid]

    def load_users(self, tenant):
        string_content = self.aws.read_text_obj(f"{tenant}/serverfiles/residents.json")
        json_obj = json.loads(string_content)
        residents = json_obj['residents']
        self.reset_tenant_user_dict(tenant)
        for resident in residents:
            user = User(
                f"{tenant}{SEPARATOR_CHAR}{resident['userid']}",
                resident['userid'],
                resident['password'],
                resident['name'],
                resident['email'],
            )
            self.save_user(tenant, user)

    def save_user_and_persist(self, tenant, user):
        self.save_user(tenant, user)
        self.persist_users(tenant)

    def persist_users(self, tenant):
            userslist = []
            for user in self.tenant_dict[tenant]['users'].values():
                record = {
                    'unit': user.unit,
                    'userid': user.userid,
                    'password': user.password,
                    'name': user.name,
                    'email': user.email,
                    'startdt': user.startdt,
                    'phone': user.phone,
                    'type': user.type,
                    'ownername': user.ownername,
                    'owneremail': user.owneremail,
                    'ownerphone': user.ownerphone,
                    'owneraddress': user.owneraddress,
                    'isrental': user.isrental,
                    'emerg_name': user.emerg_name,
                    'emerg_email': user.emerg_email,
                    'emerg_phone': user.emerg_phone,
                    'emerg_has_key': user.emerg_has_key,
                    'occupants': user.occupants,
                    'oxygen_equipment': user.oxygen_equipment,
                    'limited_mobility': user.limited_mobility,
                    'routine_visits': user.routine_visits,
                    'has_pet': user.has_pet,
                    'bike_count': user.bike_count,
                    'insurance_carrier': user.insurance_carrier,
                    'valve_type': user.valve_type,
                    'no_vehicles': user.no_vehicles,
                    'vehicles': user.vehicles,
                    'last_update_date': user.last_update_date,
                    'notes': user.notes
                }
                userslist.append(record)
            residents = {'residents': userslist}
            json_obj = json.dumps(residents, indent=2)
            self.aws.upload_text_obj(f"{tenant}/serverfiles/residents.json", json_obj)
