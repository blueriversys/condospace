"""
   Defines classes and variables related to the handling of users.
"""

import os
import json
from flask_login import UserMixin
from werkzeug.utils import secure_filename

SEPARATOR_CHAR = "@"

class User(UserMixin):
    def __init__(self, id, unit, tenant, userid, password, name, email, startdt, phone, type, ownername,
                 owneremail, ownerphone, owneraddress, isrental, emerg_name, emerg_email, emerg_phone, emerg_has_key, occupants, oxygen_equipment,
                 limited_mobility, routine_visits, has_pet, bike_count, insurance_carrier, valve_type, no_vehicles, vehicles, last_update_date, notes, active=True):
        self.id = id
        self.unit = unit
        self.tenant = tenant
        self.userid = userid
        self.password = password
        self.name = name
        self.email = email
        self.startdt = startdt
        self.phone = phone
        self.type = type
        self.ownername = ownername
        self.owneremail = owneremail
        self.ownerphone = ownerphone
        self.owneraddress = owneraddress
        self.isrental = isrental
        self.emerg_name = emerg_name
        self.emerg_email = emerg_email
        self.emerg_phone = emerg_phone
        self.emerg_has_key = emerg_has_key
        self.occupants = occupants
        self.oxygen_equipment = oxygen_equipment
        self.limited_mobility = limited_mobility
        self.routine_visits = routine_visits
        self.has_pet = has_pet
        self.bike_count = bike_count
        self.insurance_carrier = insurance_carrier
        self.valve_type = valve_type
        self.no_vehicles = no_vehicles
        self.vehicles = vehicles
        self.last_update_date = last_update_date
        self.notes = notes
        self.active = active

    def get_json_data(self):
        user = {
            'unit': self.unit,
            'tenant': self.tenant,
            'userid': self.userid,
            'name': self.name,
            'password': self.password,
            'email': self.email,
            'startdt': self.startdt,
            'phone': self.phone,
            'type': self.type,
            'ownername': self.ownername,
            'owneremail': self.owneremail,
            'ownerphone': self.ownerphone,
            'owneraddress': self.owneraddress,
            'isrental': self.isrental,
            'emerg_name': self.emerg_name,
            'emerg_email': self.emerg_email,
            'emerg_phone': self.emerg_phone,
            'emerg_has_key': self.emerg_has_key,
            'occupants': self.occupants,
            'oxygen_equipment': self.oxygen_equipment,
            'limited_mobility': self.limited_mobility,
            'routine_visits': self.routine_visits,
            'has_pet': self.has_pet,
            'bike_count': self.bike_count,
            'insurance_carrier': self.insurance_carrier,
            'valve_type': self.valve_type,
            'no_vehicles': self.no_vehicles,
            'vehicles': self.vehicles,
            'last_update_date': self.last_update_date,
            'notes': self.notes
        }
        return user

    def get_id(self):
        return self.id

    def get_unit(self):
        return self.unit

    def get_tenant(self):
        return self.tenant

    def get_userid(self):
        return self.userid

    def get_password(self):
        return self.password

    def get_name(self):
        return self.name

    def get_email(self):
        return self.email

    def get_startdt(self):
        return self.startdt

    def get_phone(self):
        return self.phone

    def get_type(self):
        return self.type

    def get_ownername(self):
        return self.owner

    def get_owneremail(self):
        return self.owneremail

    def get_ownerphone(self):
        return self.ownerphone

    def get_owneraddress(self):
        return self.owneraddress

    def get_isrental(self):
        return self.isrental

    def get_emerg_name(self):
        return self.emerg_name

    def get_emerg_email(self):
        return self.emerg_email

    def get_emerg_phone(self):
        return self.emerg_phone

    def get_emerg_has_key(self):
        return self.emerg_has_key

    def get_occupants(self):
        return self.occupants

    def get_oxygen_equipment(self):
        return self.oxygen_equipment

    def get_limited_mobility(self):
        return self.limited_mobility

    def get_routine_visits(self):
        return self.routine_visits

    def get_has_pet(self):
        return self.has_pet

    def get_bike_count(self):
        return self.bike_count

    def get_insurance_carrier(self):
        return self.insurance_carrier

    def get_valve_type(self):
        return self.valve_type

    def get_no_vehicles(self):
        return self.no_vehicles

    def get_vehicles(self):
        return self.vehicles

    def get_last_update_date(self):
        return self.last_update_date

    def get_notes(self):
        return self.notes

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

    # unit is used as nothing more than a sequence number
    def get_last_unit(self, tenant_id):
        if not self.tenant_dict[tenant_id]:
           return None
        last_unit = 0
        for user in self.get_users(tenant_id):
            if user.unit > last_unit:
                last_unit = user.unit
        return last_unit

    # def get_user_by_composite_id(self, composite_id):
    #     ind = composite_id.find('-')
    #     tenant_id = composite_id[:ind]
    #     user_id = composite_id[ind+1:]
    #     print(f"{tenant_id}  {user_id}")
    #     return self.get_user_by_userid(tenant_id, user_id)

    def get_user_by_unit(self, tenant_id, unit):
        for user in self.get_users(tenant_id):
            if user.unit == unit:
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
                resident['unit'],
                tenant,
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


class UsersUtils:
    def __init__(self):
        self.user_dict = dict()
        self.identifier = 0

    def get_user_by_userid(self, userid):
        for key in self.get_users():
            user = self.get_user_by_unit(key)
            if user.userid == userid:
                return user
        return None

    def get_users(self):
        pass

    def get_user_by_unit(self, unit):
        pass


