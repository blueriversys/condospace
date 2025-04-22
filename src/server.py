"""
https://kanishkvarshney.medium.com/hosting-your-flask-web-application-on-godaddy-5628a60e7151
https://towardsdatascience.com/virtual-environments-104c62d48c54

How to set the virtual env:
. python3 -m venv <virtual-env-folder>  (ex. python3 -m venv myvenv)
. or
. virtualenv venv -p python3.7 (whichever you want)
. source myvenv/bin/activate (to activate)
. to deactivate current virtual environment: deactivate
. pip freeze > requirements.txt (creates a requirements.txt)
. pip install -r requirements.txt
. pip show pyrebase4

To see all versions of Python in your machine:
   compgen -c python | sort -u

This has some interesting tips on how to set up Firebase:
https://pythonalgos.com/python-firebase-authentication-integration-with-fastapi/

These are the commands to install Firebase libraries:
. pip install pyrebase4
. pip install firebase-admin
. pip install requests-toolbelt==0.10.1

To run the server program:
   To run this program, issue the following in the command line:
   gunicorn --workers=1 --threads=4 --keep-alive=65 --bind=0.0.0.0:5000 server:app

To test the Portuguese site:
curl -XGET -F "text=Welcome"  -H 'Accept-Language: pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7'     http://demo.localhost:5000/about
"""

import staticvars
#from supporting_programs.image_test import img_bytes
from users import User, UsersRepository
from pdf import PDF
from datetime import timedelta, datetime
import time
import calendar
from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import os
from glob import glob
from werkzeug.utils import secure_filename
import smtplib
import cgitb
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from random import randint
from uuid import uuid4
from aws import AWS
from PIL import Image
from io import BytesIO
from redmail import gmail
from flask_babel import Babel, gettext, lazy_gettext, _
from flask_babel import format_decimal
import requests

''' for simulation of long running tasks '''
from threading import Thread, Lock
from time import sleep

#import logging
# https://realpython.com/python-logging/
#logging.basicConfig(filename='whitegate.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#prevents http server messages from going to the log file
#logging.getLogger('werkzeug').disabled = True

app = Flask(
            __name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates'
           )

login_manager = LoginManager(app)
login_manager.login_view = 'login_tenant'
login_manager.refresh_view = 'login_tenant'
login_manager.needs_refresh_message = (u'Due to inactivity, you have been logged out. Please login again')
login_manager.login_message = lazy_gettext('Login is required to access the page you want')
login_manager.needs_refresh_message_category = 'info'

CONFIG_FOLDER = 'config'
SERVER_FOLDER = 'serverfiles'
UPLOADED_FOLDER = 'uploadedfiles'
PROTECTED_FOLDER = f"{UPLOADED_FOLDER}/protected"
UNPROTECTED_FOLDER = f"{UPLOADED_FOLDER}/unprotected"

# all files in the "config" folder
# when running locally, the "config" folder must be in the File System
# when running on the cloud, the "config" folder is in the docker file
CONFIG_FILE =   f"{CONFIG_FOLDER}/config.json"

# all files in the "serverfiles" folder
INFO_FILE =     "info.json"
FINES_FILE =  "fines.json"
RESERVATIONS_FILE =  f"{UNPROTECTED_FOLDER}/reservations/reservations.json"
LINKS_FILE =    f"{SERVER_FOLDER}/links.json"
ANNOUNCS_FILE = f"{UNPROTECTED_FOLDER}/announcs/announcs.json"
LOG_FILE =      f"{SERVER_FOLDER}/messages.log"
RESIDENTS_FILE = f"{SERVER_FOLDER}/residents.json"


CENSUS_FORM_PDF_FILE_NAME = 'census_form.pdf'
CENSUS_FORMS_PDF_FULL_PATH = f"{PROTECTED_FOLDER}/docs/other/{CENSUS_FORM_PDF_FILE_NAME}"
LISTINGS_FILE = f"{UNPROTECTED_FOLDER}/listings/listings.json"
EVENT_PICS_FILE = f"{UNPROTECTED_FOLDER}/eventpics/eventpics.json"
BUCKET_PREFIX = "customers"
TENANT_NOT_FOUND = "tenant_not_found"
email_percent = 1

# strings
CENSUS_FORMS_DATE_STRING = "census_forms_pdf_date"
CONDO_NAME_STRING = "condo_name"
CONDO_LOCATION_STRING = "condo_location"
INFO_DATA_STRING = "info_data"
USERS_LOADED_STRING = "users_loaded"

# security codes
SECURITY_SUCCESS_CODE = 0
TENANT_NOT_FOUND_CODE = 1
USER_NOT_AUTHENTICATED_CODE = 2

COVER_PREF_WIDTH = 120
COVER_PREF_HEIGHT = 80

ACCEPTED_GRAPHIC_FILE_TYPES = (".jpg", ".jpeg", ".png", ".gif")

# for PROD, change the file serverfiles/config-prod.dat
with open(CONFIG_FILE, 'r') as f:
    config_file_content = f.read()
    config = json.loads(config_file_content)['config']
    print(f"\nSome of the config vars:")
    print(f"API Url: {config['api_url']}")
    print(f"API app type: {config['api_app_type']}")
    print(f"AWS bucket name: {config['bucket_name']}")
    print(f"Domain name: {config['domain']}")
    print(f"Version #: {config['version']['number']},  version date: {config['version']['date']}")

app.config['SECRET_KEY'] = config['flask_secret_key']
app.url_map.strict_slashes = False

WHITEGATE_EMAIL = config['WHITEGATE_EMAIL']
WHITEGATE_NAME = config['WHITEGATE_NAME']
GMAIL_WHITEGATE_EMAIL = config['GMAIL_WHITEGATE_EMAIL']
GMAIL_BLUERIVER_EMAIL = config['GMAIL_BLUERIVER_EMAIL']
CONTACT_TARGET_EMAIL = config['CONTACT_TARGET_EMAIL']
GMAIL_BLUERIVER_EMAIL_APP_PASSWORD = config['GMAIL_BLUERIVER_EMAIL_APP_PASSWORD']
BLUERIVER_CONTACT_EMAIL = config['BLUERIVER_CONTACT_EMAIL']
BLUERIVER_CONTACT_PASSWORD = config['BLUERIVER_CONTACT_PASSWORD']

aws = AWS(BUCKET_PREFIX, config['bucket_name'], config['aws_access_key_id'], config['aws_secret_access_key'])

# define user repository
users_repository = UsersRepository(aws)

# global tenant var (used in some routines)
tenant_global = ""

# 'user' : user, 'last_active': datetime.now()
logged_in_users = dict()

# to cache the content of any JSON file
# the key is tenant + file name
json_file_cache = {}

# to cache the content of any JSON file with not under tenant
# the key is file name
json_file_cache_no_tenant = {}

# to cache the docs file
# the key is tenant + file name
doc_files_cache = {}



# define the lock object
lock = Lock()

cgitb.enable()


condo_not_found_text = """
<html>
<body>
<div class="main">

  <div class="content">

    <div class="section-title" data-aos="zoom-out">
      <h1 class="center">Condominium Not Found</h1>
    </div>

    <div class="about-style">
          <div class="about-body">
            <div class="shadow p-3 mb-5 bg-white rounded">
                    <!--
                    <div class="center">
                        <img style="width= 95%; max-width: 300px;" src="{{ url_for('static', filename='common/img/BlueRiverLogo.gif') }}">
                    </div>
                    -->
                    <div>
                        Condominium <b>"{tenant}"</b> not found in our system. Please verify the exact spelling and enter it in the browser's address field.
                        It seems like you are not yet a customer. Please visit our Registration page to try the application out for 30 days: <a href="https://condospace.app/regis/register_en">https://condospace.app/regis/register_en</a> or
                        <a href="https://condospace.app/regis/registrar_portugues">https://condospace.app/regis/registrar_portugues</a>
                    </div>
                    <p>
                    <b>Here's how it works:</b>
                    <div class="spacer"></div>
                    <ol>
                        <li>You can access the "demo" website right now <a href="https://condospace.app/monetalphaville" target="blank">https://condospace.app/monetalphaville</a>, no login required. Accessing it that way shows you what everyone
                      in the public sees.</li>
                        <li>But if you contact us, we'll provide you a couple of login credentials so you can experience what an "admin" user would be
                      able to do, and what a "regular" resident would be able to do.</li>
                        <li>Another way is to try the service for a month to see if it works for you.</li>
                    </ol>

                    <p>

                    <b>Some of the benefits:</b>
                    <ol>
                        <li>Sense of belonging and community</li>
                        <li>Resident Census Card</li>
                        <li>Communication between Association and Residents</li>
                        <li>Easy access to documents in PDF format such as Bylaws, Rules and Regulations, Financial Statements, etc.</li>
                        <li>Web presence: suppose your condominium is called Hill Top Condominium, you can choose the first portion of
                            your domain; so a complete address could be http://condospace.app/hilltop</li>
                        <li>Ability to list apartments for sale with pictures (especially useful for FSBOs)</li>
                    </ol>
                    <div class="spacer"></div>
                    Why wait? It's much more affordable than you think. Contact us and we'll get you started.

                    <div class="spacer"></div>
                    <!--
                    <div class="center">
                        <img style="width= 95%; max-width: 360px;" src="{{ url_for('static', filename='common/img/contact.png') }}">
                    </div>
                    -->
            </div>
          </div> <!-- closes about-body box -->
    </div> <!-- closes about-style box -->

  </div> 

</div> <!-- close main -->
</body>
</html>
"""

def is_valid_graphic_file(file_name):
    f_name, f_ext = os.path.splitext(file_name)
    f_ext = f_ext.lower()
    if f_ext not in ACCEPTED_GRAPHIC_FILE_TYPES:
        return False
    return True

def is_tenant_found(tenant):
    if not aws.is_file_found(f"{INFO_FILE}"):
        return False
    info_json = get_json_from_file_no_tenant(f"{INFO_FILE}")
    if tenant in info_json['config']:
        if not is_tenant_folder_found(tenant):
            return False
        global tenant_global
        tenant_global = tenant
        return True
    return False

def is_tenant_folder_found(tenant):
    if not aws.is_file_found(f"{tenant}/{RESIDENTS_FILE}"):
        return False
    return True

def get_doc_files_cache(tenant, path, pattern):
    key = f"{tenant}-{path}"
    if key in doc_files_cache:
        print(f"key {key} found. return doc_files from cache")
        return doc_files_cache[key]

    docs = get_files(tenant, path, pattern)
    doc_files_cache[key] = docs
    print(f"key {key} not found in cache. return doc_files from aws")
    return doc_files_cache[key]

def invalidate_doc_files_cache(tenant, path):
    key = f"{tenant}-{path}"
    if key in doc_files_cache:
        del doc_files_cache[key]  # to force an aws read next time
        print(f"key {key} found. doc_files_cache invalidated")
    else:
        print(f"key {key} not found in cache. No deletion")

def get_json_from_file(tenant, file_path):
    key = f"{tenant}-{file_path}"
    if key in json_file_cache:
        print(f"return from cache, key: {key}")
        return json.loads(json_file_cache[key])

    full_path = f"{tenant}/{file_path}"
    if not aws.is_file_found(full_path):
        return None

    string_content = aws.read_text_obj(full_path)
    json_file_cache[key] = string_content
    json_obj = json.loads(string_content)
    print(f"return from file, storing key: {key}")
    return json_obj

def save_json_to_file(tenant, file_path, content):
    string_content = json.dumps(content, indent=4, ensure_ascii=False)
    resp = aws.upload_text_obj(f"{tenant}/{file_path}", string_content)
    key = f"{tenant}-{file_path}"
    global json_file_cache
    #print(f"cached to mem: {key}, {string_content}")
    json_file_cache[key] = string_content
    return resp

def get_json_from_file_no_tenant(file_path):
    if file_path in json_file_cache_no_tenant:
        print(f"file_no_tenant: returning mem content")
        return json.loads(json_file_cache_no_tenant[file_path])

    if not aws.is_file_found(file_path):
        return None

    string_content = aws.read_text_obj(file_path)
    json_file_cache_no_tenant[file_path] = string_content
    return json.loads(string_content)

def save_json_to_file_no_tenant(file_path, content):
    str_content = json.dumps(content, indent=4, ensure_ascii=False)
    aws.upload_text_obj(f"{file_path}", str_content)
    print(f"file_no_tenant: returning file content")
    global json_file_cache_no_tenant
    json_file_cache_no_tenant[file_path] = str_content


def get_tenant():
    url = request.path
    if url.count('/') == 1:
        tenant = 'root'
    else:
        tenant = url[1:]
        bar_pos = tenant.find('/')
        tenant = tenant[0 : bar_pos]

    tenant = tenant.lower()
    #print(f"in get_tenant(): url {url}   tenant: {tenant}")

    if tenant == config['domain']:
        tenant = 'root'
    if tenant != 'root' and not is_tenant_found(tenant):
        tenant = TENANT_NOT_FOUND
    #log(f"header host: {url},   tenant: {tenant},  domain: {config['domain']}")
    return tenant

# in info_data we return only that specific tenant's info data
def get_info_data(tenant):
    if not aws.is_file_found(f"{INFO_FILE}"):
        print(f"get_info_data(): file not found: {INFO_FILE},  tenant: {tenant}")
        return None

    try:
        json_obj = get_json_from_file_no_tenant(f"{INFO_FILE}")
        if tenant in json_obj['config']:
            info_data = json_obj['config'][tenant]
        else:
            return None
        if current_user.is_anonymous:
            is_authenticated = False
        else:
            is_authenticated = True if current_user.tenant == tenant else False
        info_data['is_authenticated'] = is_authenticated
        # session[INFO_DATA_STRING] = info_data
        info_data['loggedin-userdata'] = get_current_user_data()
        return info_data
    except:
        print(f"get_info_data(): unable to get info for tenant: {tenant}, file {INFO_FILE}")
        log(tenant, f"Error trying to read file {INFO_FILE}")
        return None


def get_current_user_data():
    if current_user.is_anonymous:
        return None
    user_data = {
        'id': current_user.id,
        'userid': current_user.userid,
        'unit': current_user.unit,
        'name': current_user.name,
        'email': current_user.email,
        'tenant': get_tenant()
    }
    return user_data

def get_lat_long(address):
    address = address.replace(', ', ' ')
    address = address.replace(',', ' ')
    pieces = address.split(" ")
    pieces_str = ''
    for piece in pieces:
        pieces_str += f"+{piece}"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={pieces_str}&key={config['google_maps_api_key']}"
    headers = {'Content-Type': 'application/json'}
    response_json = requests.post(url, headers=headers)
    #print("JSON response:", response_json.json())
    addr_dict = json.loads(response_json.text)
    lat = None
    long = None

    if addr_dict is not None and addr_dict['status'] != 'ZERO_RESULTS':
        # print(f"api response: {addr_dict}")
        if 'location' in addr_dict['results'][0]['geometry']:
            lat = addr_dict['results'][0]['geometry']['location']['lat']
            long = addr_dict['results'][0]['geometry']['location']['lng']

    return lat, long

def add_to_logged_in_users(tenant, user):
    print(f"here in add_to_logged_in_users()")
    global logged_in_users
    if user.id not in logged_in_users:
        print(f"adding composite user id {user.id}")
        logged_in_users[user.id] = { 'user': user, 'tenant': tenant, 'last_active': datetime.now() }
    else:
        logged_in_users[user.id]['last_active'] = datetime.now()

def remove_from_logged_in_users(user):
    print(f"here in remove_from_logged_in_users()")
    if user.id in logged_in_users:
        del logged_in_users[user.id]
        print(f"deleted user {user.id} from logged_in_users")
    return

def is_user_logged_in(tenant, user):
    if user.is_anonymous:
        print("in is_user_logged_in(): user is anonymous")
        return False
    global logged_in_users
    # print(f"is_user_logged_in(), step 1, user.id: {user.id}")
    # print(f"is_user_logged_in(), logged_in_users: {logged_in_users}")
    if user.id not in logged_in_users:
        print(f"in is_user_logged_in(): {user.id} not in logged in users")
        return False
    if logged_in_users[user.id]['tenant'] != tenant:
        print(f"in is_user_logged_in(): {user.id} for tenant {tenant} not in logged in users")
        return False

    time1 = logged_in_users[user.id]['last_active']
    if (datetime.now() - time1) > timedelta(hours=2):
        del logged_in_users[user.id]
        return False
    return True


def image_to_byte_array(image: Image, img_format: str) -> bytes:
    # BytesIO is a file-like buffer stored in memory
    img_byte_arr = BytesIO()
    # image.save expects a file-like as a argument
    if image.format is None:
        image.format = img_format
    image.save(img_byte_arr, format=image.format)
    # Turn the BytesIO object back into a bytes object
    return img_byte_arr.getvalue()

def get_format_and_size(img_bytes):
    cover_image = Image.open(BytesIO(img_bytes))
    w, h = cover_image.size
    return (cover_image.format, w, h)

def reduce_image_enh(img_bytes, nw, nh):
    cover_image = Image.open(BytesIO(img_bytes))
    img_format = cover_image.format
    resized_img = cover_image.resize((nw, nh), Image.Resampling.LANCZOS)
    img_bytes = image_to_byte_array(resized_img, img_format)
    return img_format, img_bytes

def get_unit_list(include_adm=True):
    def sort_by_userid(obj):
        return obj['userid']
    load_users(get_tenant())
    unit_list = []
    for user in users_repository.get_users(get_tenant()):
        if user.type == staticvars.USER_TYPE_ADMIN and include_adm == False:
            continue
        unit_list.append({'unit': user.unit, 'userid': user.userid, 'res_name': user.name, 'contact': user.email, 'phone': user.phone})
    unit_list.sort(key=sort_by_userid)
    return unit_list

def build_condo_not_found(tenant):
    # return render_template("condo_not_found.html")
    condo_not_found_html = condo_not_found_text.replace('{tenant}', tenant)
    lock.release()
    return condo_not_found_html


'''
 Read the residents
 json file from disk and fill a user dict
'''
def load_users(tenant):
    if users_repository.is_tenant_loaded(tenant):
        return
    print(f"load_users(): tenant {tenant}")
    users_repository.load_users(tenant)
    print(f"just loaded tenant {tenant} into users_repository")


''' These are long running related functions '''
def email_task(email_list, subject, body):
    global email_percent
    total_count = len(email_list)
    #print(f" total count {total_count}")
    count = 0
    for single_email_to in email_list:
#        send_email_relay_host(single_email_to, subject, body)
        send_email_redmail()
        count += 1
        email_percent = int( (count / total_count ) * 100 )
        #sleep(2)

    #   FOR TESTING PURPOSES ONLY
    #    for single_email_to in emailto:
    #        print(f'sending email to {single_email_to}')
    #        subj = mailObj['request']['subject']
    #        subject = subj + ",   " + single_email_to
    #        single_email_to = GMAIL_WHITEGATE_EMAIL
    #        send_email_relay_host(single_email_to, subject, body)

    email_percent = 100


'''
  will send email to all residents, one by one
'''
@app.route('/sendmail', methods=['POST'])
def send_email_to_all(tenant, subject, body):
    email_list = []
    for user in users_repository.get_users(tenant):
        if user.get_email():
            email_list.append(user.get_email())
    print(f"email count to be sent: {len(email_list)}")
    global email_percent
    email_percent = 1
    # t1 = Thread(target=email_task, args=(email_list, subject, body))
    # t1.start()
    send_email_redmail_all(email_list, subject, body)
    status = {'percent': email_percent}
    return json.dumps(status)

@app.route('/getstatus', methods=['GET'])
def get_status():
    status = {'percent': email_percent}
    return json.dumps(status)


'''
  These are folder related routes
  for PROTECTED files
'''
@app.route('/<tenant>/docs/<path:rel_path>')
@login_required
def protected(tenant, rel_path):
    # print(f"in protected(): tenant: {tenant}, rel_path {rel_path}")
    # print(f"full path: {tenant}/{PROTECTED_FOLDER}/docs/{rel_path}")
    file_obj = aws.read_binary_obj(f"{tenant}/{PROTECTED_FOLDER}/docs/{rel_path}")
    #TODO: rather than returning "application/pdf", test the file type first
    return Response(response=file_obj, status=200, mimetype="application/pdf")


'''
  These are folder related routes
  for UNPROTECTED files
'''
@app.route('/favicon.ico')
def favicon_request():
    #print(f"here in favicon_request()")
    return send_from_directory('static/img', 'favicon.png')

@app.route('/<tenant>/opendocs/<path:rel_path>')
def unprotected(tenant, rel_path):
    #print(f"in unprotected(): tenant: {tenant}, rel_path {rel_path}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/opendocs/{rel_path}")
    #TODO: rather than returning "application/pdf", test the file type first
    return Response(response=file_obj, status=200, mimetype="application/pdf")

# Custom static data
@app.route('/<tenant>/pics/<filename>')
def custom_static(tenant, filename):
#    return send_from_directory(UNPROTECTED_FOLDER + '/pics', filename)
    #print(f"in custom_static(): tenant: {tenant}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/pics/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<tenant>/listings/<unit>/<listing_id>/pics/<filename>')
def custom_static_listing(tenant, unit, listing_id, filename):
    print(f"in custom_static_listing(): tenant: {tenant}, unit {unit}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/listings/{unit}/{listing_id}/pics/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<tenant>/reservations/<amenity_id>/<filename>')
def custom_static_amenity(tenant, amenity_id, filename):
    print(f"in custom_static_amenity(): tenant: {tenant}, amenity_id {amenity_id}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/reservations/amenity_{amenity_id}.jpg")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<tenant>/announcs/<filename>')
def custom_static_announc(tenant, filename):
    print(f"in custom_static_announc(): tenant: {tenant}, filename {filename}")
    _, file_ext = os.path.splitext(filename)
    if file_ext == '.jpg':
        mtype = "image/jpeg"
    elif file_ext == ".png":
        mtype = "image/png"
    elif file_ext == ".pdf":
        mtype = "application/pdf"
    elif file_ext == '.doc':
        mtype = "application/msword"
    elif file_ext == '.odt':
        mtype = 'application/vnd.oasis.opendocument.text'
    else:
        mtype = "text/plain"

    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/announcs/{filename}")
    return Response(response=file_obj, status=200, mimetype=mtype)

@app.route('/<tenant>/event/eventpics/<title>/pics/<filename>')
def custom_static_event(tenant, title, filename):
    #print(f"in custom_static_event(): tenant: {tenant}, title {title}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/eventpics/{title}/pics/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<tenant>/branding/<filename>')
def custom_static_branding(tenant, filename):
#    return send_from_directory(UNPROTECTED_FOLDER + '/pics', filename)
    #print(f"custom_static_branding(): tenant {tenant}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/branding/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<tenant>/logos/<filename>')
def custom_logos(tenant, filename):
#    return send_from_directory(UNPROTECTED_FOLDER + '/logos', filename)
    #print(f"custom_logos(): tenant {tenant}, filename {filename}")
    file_obj = aws.read_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/logos/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/common/<path:rel_path>')
def common_static_images(rel_path):
    print(f"in common_static_images(): rel_path: {rel_path}")
#    return send_from_directory('static', rel_path)
    return send_from_directory('static', f"{rel_path}")

'''
  These are GET request routes
'''
# @app.route('/<tenant>')
# def tenant_only_home(tenant):
#     lock.acquire()
#     print(f"in tenant_only_home()  tenant: {tenant}")
#     if not is_tenant_found(tenant):
#         lock.release()
#         return render_template("condo_not_found.html", tenant=tenant)
#     info_data = get_info_data_tenant(tenant)
# #    session[INFO_DATA_STRING] = None
#     lock.release()
#     return render_template("home.html", user_types=staticvars.user_types, info_data=info_data)

@app.route('/')
def home_root():
    print("here in server.home_root()")
    return redirect("/regis/registrar_portugues")

@app.route('/health')
def home_health():
    print("here in server.home_health()")
    return "OK"

@app.route('/<tenant>')
def home_tenant(tenant):
    print(f"here in server.home_tenant(). tenant {tenant}")
    if tenant == 'admin':
        return redirect(f"/admin/root")
    elif tenant == 'regis':
        return redirect(f"/regis/root")

    return redirect(f"{tenant}/home")

@app.route('/<tenant>/home')
def home(tenant):
    lock.acquire()
    print(f"in server.home():  tenant: {tenant}")
    if not is_tenant_found(tenant):
        return build_condo_not_found(tenant)
    info_data = get_info_data(tenant)
#    session[INFO_DATA_STRING] = None
    lock.release()
    return render_template("home.html", user_types=staticvars.user_types, info_data=info_data)


def check_security(tenant):
    ret_page = ''
    error_code = SECURITY_SUCCESS_CODE
    # first, check if the tenant exists
    if not is_tenant_found(tenant):
        error_code = TENANT_NOT_FOUND_CODE
        ret_page = render_template("condo_not_found.html", tenant=tenant)

    # check of the client has another session with a user logged in
    if current_user.is_authenticated and current_user.tenant != tenant:
        error_code = USER_NOT_AUTHENTICATED_CODE
        ret_page = redirect(f"/{tenant}/home")

    # check of the client has another session with a user logged in
    if not current_user.is_authenticated:
        error_code = USER_NOT_AUTHENTICATED_CODE

    return ret_page, error_code


@app.route('/<tenant>/setup')
@login_required
def setup(tenant):
    lock.acquire()

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    # we need to disable this for now
    # if not is_user_logged_in(tenant, current_user):
    #     print(f"setup(): user not logged in, redirecting to the login page...")
    #     lock.release()
    #     return redirect(f"login")
    #
    # print(f"setup: user is logged in: {logged_in_users}")

    # now test if the user making the request is logged in
    # if not is_user_logged_in(current_user):
    #     print("user not logged in")
    #     lock.release()
    #     return redirect(f"login")

    info_data = get_info_data(tenant)
    units = get_unit_list()
    lock.release()
    return render_template("setup.html", tenant=tenant, units=units, info_data=info_data)


#------------------------------------------------------------------------------------------
#   Reservations related routes
#------------------------------------------------------------------------------------------
@app.route('/<tenant>/reservations')
@login_required
def get_reservations(tenant):
    lock.acquire()
    print(f"here in get_reservations")

    # page, check_code = check_security(tenant)
    # if check_code != SECURITY_SUCCESS_CODE:
    #     lock.release()
    #     return page
    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    info_data = get_info_data(tenant)
    amenities_dict = {}
    rsv_dict = {}

    # test if the amenities file exists
    if aws.is_file_found(f"{tenant}/{RESERVATIONS_FILE}"):
        rsv_content = get_json_from_file(tenant, RESERVATIONS_FILE)
        if 'amenities' in rsv_content:
            amenities = rsv_content['amenities']
            if len(amenities) > 0:
                for key, amenity in amenities.items():
                    amenity['created_on'] = get_string_from_epoch(amenity['created_on'], info_data['language'])
                amenities_dict = amenities.items()

        if 'reservations' in rsv_content:
            reservations = rsv_content['reservations']
            if len(reservations) > 0:
                for user_id, reservation in reservations.items():
                    for rsv_id, rsv_data in reservation['reservations'].items():
                        rsv_data['created_on'] = get_string_from_epoch(rsv_data['created_on'], info_data['language'])
                        rsv_name = users_repository.get_user_by_userid(tenant, user_id).name
                        arr_entry = {"name": rsv_name, "user_id": user_id, "rsv_id": rsv_id, "date": rsv_data['date'],
                                     "time_from": rsv_data['time_from'], "time_to": rsv_data['time_to']}
                        amenity_id = rsv_data['amenity_id']
#                        print(f"this is arr_entry: {arr_entry}")
                        if amenity_id in rsv_dict:
                            rsv_dict[amenity_id].append(arr_entry)
                        else:
                            rsv_dict[amenity_id] = [arr_entry]


#    print(f"\n\n rsv_dict: {rsv_dict} \n\n")

    # sort reservations by date and time
    if len(rsv_dict) > 0:
        for amenity_id, reservations in rsv_dict.items():
            reservations.sort(key=sort_reservation)

    units = get_unit_list()
    lock.release()
    return render_template("reservations.html", tenant=tenant, units=units, reservations=rsv_dict, amenities=amenities_dict, user_types=staticvars.user_types, info_data=info_data)

def sort_reservation(rsv):
    date = get_epoch_from_string(f"{rsv['date']['y']}-{rsv['date']['m']}-{rsv['date']['d']}")
    time_from_h = rsv['time_from']['h']
    time_from_m = rsv['time_from']['m']
    return date, time_from_h, time_from_m


@app.route('/<tenant>/save_amenity', methods=["POST"])
@login_required
def save_amenity(tenant):
    lock.acquire()
    print(f"here in save_amenity()")
    tenant_req = request.form['tenant']

    if tenant != tenant_req:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = request.form['created_by']
    descr = request.form['descr']
    use_default_img = True if request.form['use_default_img'] == 'yes' else False
    paid_amenity = request.form['paid_amenity']
    send_email = request.form['send_email']

    print(f" paid: {paid_amenity},  send email: {send_email}")

    amenity_entry = {
        "descr": descr,
        "created_by": user_id,
        "created_on": get_epoch_from_now(),
        "paid_amenity": paid_amenity,
        "send_email": send_email
    }

    # read the RESERVATIONS_FILE to add a condo to it
    if aws.is_file_found(f"{tenant}/{RESERVATIONS_FILE}"):
        rsv_content = get_json_from_file(tenant, RESERVATIONS_FILE)
        if 'reservations' in rsv_content:
            reservations = rsv_content['reservations']
        else:
            reservations = {}

        if 'amenities' in rsv_content:
            amenities = rsv_content['amenities']

            # find the last amenity_id
            amenity_id = 0
            for id, value in amenities.items():
                id = int(id)
                amenity_id = id if id > amenity_id else amenity_id
            amenity_id += 1
            amenities[amenity_id] = amenity_entry
        else:
            amenity_id = 0
            amenities = { amenity_id : amenity_entry }
    else:
        amenity_id = 0
        amenities = { amenity_id : amenity_entry }
        reservations = {}

    if use_default_img:
        pic_file_name = os.path.basename(request.form['default_img_name'])
        print(f"static folder: {app.static_folder}    pic file: {pic_file_name}")
        amenity_pic = open(f"{app.static_folder}/img/{pic_file_name}", "rb")
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/reservations/amenity_{amenity_id}.jpg", amenity_pic.read())
    else:
        amenity_pic = request.files['amenity_pic']
        amenity_pic.stream.seek(0)
        img_bytes = amenity_pic.read()
        _, img_bytes = reduce_image_enh(img_bytes, COVER_PREF_WIDTH, COVER_PREF_HEIGHT)
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/reservations/amenity_{amenity_id}.jpg", img_bytes)

    data_to_persist = {"reservations": reservations, "amenities": amenities}
    save_json_to_file(tenant, RESERVATIONS_FILE, data_to_persist )
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/delete_amenity', methods=["POST"])
def delete_amenity(tenant):
    lock.acquire()
    print(f"in delete_amenity(): tenant {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    prefix = "amenity"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    amenity_id = json_obj[prefix]['amenity_id']
    found_rsv = False

    # make sure there is no reservation for the amenity to be deleted
    if aws.is_file_found(f"{tenant}/{RESERVATIONS_FILE}"):
        rsv_content = get_json_from_file(tenant, RESERVATIONS_FILE)
        if 'reservations' in rsv_content:
            reservations = rsv_content['reservations']
        else:
            reservations = {}

        if 'amenities' in rsv_content:
            amenities = rsv_content['amenities']
        else:
            # there is nothing to delete, let's return success
            return_obj = json.dumps({'response': {'status': 'success'}})
            lock.release()
            return return_obj

        # let's check if there is any reservation for the amenity
        for user_id, reservation in reservations.items():
            for rsv_id, rsv_data in reservations[user_id]['reservations'].items():
                if str(rsv_data['amenity_id']) == amenity_id:
                    found_rsv = True
                    break
                else:
                    continue
    else:
        # there is nothing to delete, let's return success
        return_obj = json.dumps({'response': {'status': 'success'}})
        lock.release()
        return return_obj

    if found_rsv:
        print(f"found a reservation for the amenity_id {amenity_id}")
        return_obj = json.dumps({'response': {'status': 'found_rsv'}})
        lock.release()
        return return_obj

    # here we know there is no reservation for the amenity
    if amenity_id in amenities:
        del amenities[amenity_id]
        data_to_persist = {"reservations": reservations, "amenities": amenities}
        save_json_to_file(tenant, RESERVATIONS_FILE, data_to_persist)
        # now delete amenity picture file
        aws.delete_object(f"{tenant}/{UNPROTECTED_FOLDER}/reservations/amenity_{amenity_id}.jpg")
    else:
        print(f"amenity_id not found for tenant {tenant}")

    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/make_reservation', methods=["POST"])
@login_required
def make_reservation(tenant):
    lock.acquire()
    print(f"here in make_reservation()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_obj = request.get_json()
    prefix = "reservation"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    amenity_id = json_obj[prefix]['amenity_id']
    date_y = json_obj[prefix]['date']['y']
    date_m = json_obj[prefix]['date']['m']
    date_d = json_obj[prefix]['date']['d']
    time_from_h = json_obj[prefix]['time_from']['h']
    time_from_m = json_obj[prefix]['time_from']['m']
    time_to_h = json_obj[prefix]['time_to']['h']
    time_to_m = json_obj[prefix]['time_to']['m']
    send_email = json_obj[prefix]['send_email']

    print(f"send email: {send_email}")

    rsv_entry = {
        "created_on": get_epoch_from_now(),
        "amenity_id": amenity_id,
        "date": { "y": date_y, "m": date_m, "d": date_d },
        "time_from": { "h": time_from_h, "m": time_from_m },
        "time_to":   { "h": time_to_h, "m": time_to_m }
    }

    # read the RESERVATIONS_FILE to add a reservation to it
    if aws.is_file_found(f"{tenant}/{RESERVATIONS_FILE}"):
        rsv_content = get_json_from_file(tenant, RESERVATIONS_FILE)

        if 'amenities' in rsv_content:
            amenities = rsv_content['amenities']
        else:
            # cannot make a reservation for an amenity that doesn't exist
            return_obj = json.dumps({'response': {'status': 'error'}})
            lock.release()
            return return_obj

        if 'reservations' in rsv_content:
            rsv_data = rsv_content['reservations']
            if user_id in rsv_data:
                # find the last reservation_id for the user
                rsv_id = 0
                for id, value in rsv_data[user_id]['reservations'].items():
                    id = int(id)
                    rsv_id = id if id > rsv_id else rsv_id
                rsv_id += 1
                rsv_data[user_id]['reservations'][rsv_id] = rsv_entry
            else:
                rsv_id = 0
                rsv_data[user_id] = { "reservations": {rsv_id: rsv_entry} }
        else:
            # this is the first reservation in the file
            rsv_id = 0
            rsv_data = { user_id: { "reservations": {rsv_id: rsv_entry} } }
    else:
        # if file not found, there is no amenity, therefore way to make a reservation
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    if send_email == 'true':
        user_id = amenities[str(amenity_id)]['created_by']
        user = users_repository.get_user_by_userid(tenant, user_id)
        print(f"user_id: {user.userid},  email to: {user.email}")
        info_data = get_info_data(tenant)
        send_reservation_email(info_data, user_id, user.email, amenities[str(amenity_id)]['descr'],
                               rsv_entry['date'], rsv_entry['time_from'], rsv_entry['time_to'])
    else:
        print(f"NO EMAIL TO BE SENT FOR THIS RESERVATION")

    data_to_persist = {"reservations": rsv_data, "amenities": amenities}
    save_json_to_file(tenant, RESERVATIONS_FILE, data_to_persist)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


def send_reservation_email(info_data, user_id, email, amenity_descr, date, time_from, time_to):
    if time_from['h'] < 10:
        time_from['h'] = f"0{time_from['h']}"
    if time_from['m'] < 10:
        time_from['m'] = f"0{time_from['m']}"
    if time_to['h'] < 10:
        time_to['h'] = f"0{time_to['h']}"
    if time_to['m'] < 10:
        time_to['m'] = f"0{time_to['m']}"
    if info_data['language'] == 'pt':
        subject = "Uma reserva de espaço pago acabou de ser feita"
        body = f"""
Apto {user_id} fez uma reserva do espaço [{amenity_descr}],
para a data de {date['d']}-{date['m']}-{date['y']} entre {time_from['h']}:{time_from['m']} e {time_to['h']}:{time_to['m']}.
"""
    else:
        subject = "A reservation of a for-a-fee amenity was made"
        body = f"""
User {user_id} made a reservation of amenity [{amenity_descr}],
for date {date['m']}-{date['d']}-{date['y']}, time between {time_from['h']}:{time_from['m']} to {time_to['h']}:{time_to['m']}.
"""
    send_email_redmail(email, subject, body)


@app.route('/<tenant>/delete_reservation', methods=["POST"])
@login_required
def delete_reservation(tenant):
    lock.acquire()
    print(f"here in delete_reservation()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_obj = request.get_json()
    prefix = "reservation"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    rsv_id = json_obj[prefix]['rsv_id']

#    print(f"tenant: {tenant},   user_id: {user_id},   rsv_id {rsv_id}  rsv_id type: {type(rsv_id)}")

    if aws.is_file_found(f"{tenant}/{RESERVATIONS_FILE}"):
        rsv_content = get_json_from_file(tenant, RESERVATIONS_FILE)
        if not 'amenities' in rsv_content or not 'reservations' in rsv_content:
            return_obj = json.dumps({'response': {'status': 'error'}})
            lock.release()
            return return_obj

        amenities = rsv_content['amenities']
        rsv_data = rsv_content['reservations']
    else:
        return_obj = json.dumps({'response': {'status': 'file_not_found'}})
        lock.release()
        return return_obj

    if rsv_id in rsv_data[user_id]['reservations']:
        del rsv_data[user_id]['reservations'][rsv_id]
        print(f"reservation deleted")
    else:
        return_obj = json.dumps({'response': {'status': 'rsv_not_found'}})
        lock.release()
        return return_obj

    data_to_persist = {"reservations": rsv_data, "amenities": amenities}
    save_json_to_file(tenant, RESERVATIONS_FILE, data_to_persist)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


#------------------------------------------------------------------------------------------
#   Fine related routes
#------------------------------------------------------------------------------------------
@app.route('/<tenant>/fines')
@login_required
def payments(tenant):
    lock.acquire()
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    info_data = get_info_data(tenant)
    pay_json = get_json_from_file_no_tenant(f"{FINES_FILE}")
    fines_list = []

    if pay_json is not None and tenant in pay_json['fines']:
        for user, payment in pay_json['fines'][tenant].items():
            for fine_id, fine in payment['fines'].items():
                entry = dict()
                entry['created_on'] = get_string_from_epoch(fine['created_on'], info_data['language'])
                entry["user_id"] = user
                entry["fine_id"] = fine_id
                entry["name"] = fine['name']
                entry["email"] = fine['email']
                entry['descr'] = fine['descr']
                amount = float(fine['amount'])
                entry['amount'] = f"{amount:.2f}"
                entry['due_date'] = fine['due_date']
                if 'charge_type' in fine:
                    entry['charge_type'] = fine['charge_type']
                else:
                    entry['charge_type'] = 'fine'
                entry['status'] = "unpaid" if fine['paid_date'] is None else f"paid {fine['paid_date']['d']}/{fine['paid_date']['m']}/{fine['paid_date']['y']}"
                fines_list.append(entry)

    units = get_unit_list(include_adm=False)
    lock.release()
    return render_template("fines.html", tenant=tenant, units=units, fines=fines_list, user_types=staticvars.user_types, info_data=info_data)

def get_payment_ref(issue_date, payment_id):
    issue_date_str = get_string_from_epoch_format( issue_date, '%Y-%m-%d' )
    issue_date = {'y': issue_date_str[0:4], 'm': issue_date_str[5:7], 'd': issue_date_str[8:] }
    print(f"get_payment_ref(): issue date: {issue_date}")
    return f"{issue_date['y']}{issue_date['m']}{issue_date['d']}-{payment_id}"

@app.route('/<tenant>/savefine', methods=["POST"])
def save_payment(tenant):
    lock.acquire()
    print(f"in save_payment(): tenant {tenant}")
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    tenant_json = json_obj['payment']['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj['payment']['user_id']
    name = json_obj['payment']['name']
    email = json_obj['payment']['email']
    phone = json_obj['payment']['phone']
    amount = json_obj['payment']['amount']
    descr = json_obj['payment']['descr']
    due_date_y = json_obj['payment']['due_date']['y']
    due_date_m = json_obj['payment']['due_date']['m']
    due_date_d = json_obj['payment']['due_date']['d']
    charge_type = json_obj['payment']['charge_type']

    fine_entry = {
        "created_on": get_epoch_from_now(),
        'name': name,
        'email': email,
        "descr": descr,
        "amount": float(amount),
        "paid_amount": None,
        "due_date": {"y": due_date_y, "m": due_date_m, "d": due_date_d},
        "paid_date": None,
        "charge_type": charge_type
    }

    # read the FINES_FILE to add a fine to it
    if aws.is_file_found(f"{FINES_FILE}"):
        pay_data = get_json_from_file_no_tenant(f"{FINES_FILE}")

        if tenant in pay_data['fines']:
            # find the last fine_id for the user
            if user_id in pay_data['fines'][tenant]:
                fine_id = 0
                for id, value in pay_data['fines'][tenant][user_id]['fines'].items():
                    id = int(id)
                    fine_id = id if id > fine_id else fine_id
                fine_id += 1
                pay_data['fines'][tenant][user_id]['fines'][fine_id] = fine_entry
            else:
                fine_id = 0
                pay_data['fines'][tenant][user_id] = { "name": name, "email": email, "phone": phone, "fines": { fine_id: fine_entry } }
        else:
            fine_id = 0
            pay_data['fines'] = { tenant: { user_id: { "name": name, "email": email, "phone": phone, "fines": { fine_id: fine_entry } } } }

        payment_id = fine_id
        #
        # if tenant in pay_data['fines']:
        #     if user_id in pay_data['fines'][tenant]:
        #         pay_data['fines'][tenant][user_id]['fines'][fine_id] = fine_entry
        #     else:
        #         pay_data['fines'][tenant][user_id] = { "name": name, "email": email, "phone": phone, "fines": { fine_id: fine_entry } }
        # else:
        #     pay_data['fines'] = { tenant: { user_id: { "name": name, "email": email, "phone": phone, "fines": { fine_id: fine_entry } } } }
    else:
        fine_id = 0
        payment_id = fine_id
        pay_data = { 'fines': { tenant: { user_id: { "name": name, "email": email, "phone": phone, "fines": { fine_id: fine_entry } } } } }

    save_json_to_file_no_tenant(FINES_FILE, pay_data)
    issue_date_str = get_string_from_epoch_format( fine_entry['created_on'], '%Y-%m-%d' )
    issue_date = {'y': issue_date_str[0:4], 'm': issue_date_str[5:7], 'd': issue_date_str[8:] }
    payment_ref = get_payment_ref(fine_entry['created_on'], payment_id)

    if email:
        info_data = get_info_data(tenant)
        send_payment_notification(info_data, name, email, amount, descr, issue_date, fine_entry['due_date'],
                                  charge_type, payment_ref)

    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/setpayment', methods=["POST"])
@login_required
def set_payment(tenant):
    lock.acquire()
    print(f"in set_payment(): tenant {tenant}")
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    tenant_json = json_obj['payment']['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj['payment']['user_id']
    fine_id = json_obj['payment']['fine_id']
    date_year = json_obj['payment']['date']['y']
    date_month = json_obj['payment']['date']['m']
    date_day = json_obj['payment']['date']['d']

    print(f"{date_year} / {date_month} / {date_day} {user_id} {fine_id}")

    # read the FINES_FILE to add an additional condo to it
    if not aws.is_file_found(f"{FINES_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
    else:
        pay_data = get_json_from_file_no_tenant(f"{FINES_FILE}")
        pay_data['fines'][tenant][user_id]['fines'][fine_id]['paid_date'] = { 'y': date_year, 'm': date_month, 'd': date_day }
        save_json_to_file_no_tenant(FINES_FILE, pay_data)
        return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

@app.route('/<tenant>/deletefine', methods=["POST"])
def delete_fine(tenant):
    lock.acquire()
    print(f"in delete_fine(): tenant {tenant}")
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    prefix = "fine"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    fine_id = json_obj[prefix]['fine_id']

    print(f"user {user_id}    fine_id {fine_id}")

    # read the FINES_FILE to add an additional condo to it
    if not aws.is_file_found(f"{FINES_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
    else:
        pay_data = get_json_from_file_no_tenant(f"{FINES_FILE}")
        if fine_id in pay_data['fines'][tenant][user_id]['fines']:
            del pay_data['fines'][tenant][user_id]['fines'][fine_id]
            save_json_to_file_no_tenant(FINES_FILE, pay_data)

        return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

@app.route('/<tenant>/sendfinereminder', methods=["POST"])
def send_fine_reminder(tenant):
    lock.acquire()
    print(f"in send_fine_reminder(): tenant {tenant}")
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    info_data =  get_info_data(tenant)
    json_obj = request.get_json()
    prefix = "fine"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    fine_id = json_obj[prefix]['fine_id']
    name = json_obj[prefix]['name']
    email = json_obj[prefix]['email']
    amount = json_obj[prefix]['amount']
    descr = json_obj[prefix]['descr']
    due_date_y = json_obj[prefix]['due_date']['y']
    due_date_m = json_obj[prefix]['due_date']['m']
    due_date_d = json_obj[prefix]['due_date']['d']
    charge_type = json_obj[prefix]['charge_type']

    # read the FINES_FILE to add a charge to it
    if not aws.is_file_found(f"{FINES_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    pay_data = get_json_from_file_no_tenant(f"{FINES_FILE}")
    if fine_id not in pay_data['fines'][tenant][user_id]['fines']:
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    created_on = pay_data['fines'][tenant][user_id]['fines'][fine_id]['created_on']
#    issue_date = {'y': issue_date_y, 'm': issue_date_m, 'd': issue_date_d}
    due_date = {'y': due_date_y, 'm': due_date_m, 'd': due_date_d}
    payment_ref = get_payment_ref(created_on, fine_id)
    issue_date = get_date_dict_from_epoch(created_on)
    print(f"issue date: {issue_date}")

    if email:
        send_payment_notification(info_data, name, email, amount, descr, issue_date, due_date, charge_type, payment_ref)
        print(f"end of send_contact_email()")
        return_obj = json.dumps({'response': {'status': 'success'}})
    else:
        return_obj = json.dumps({'response': {'status': 'error', 'message': 'fine has no email address'}})

    lock.release()
    return return_obj

def send_payment_notification(info_data, name, email, amount, descr, issue_date, due_date, charge_type, payment_id):
    condo_name = info_data['condo_name']
    print(f"charge type: {charge_type}")

    if charge_type == 'fine':
        title = info_data['fine_title']
        pix = info_data['pix_key']
        text = info_data['fine_template']
    else:
        title = info_data['pay_title']
        pix = info_data['pay_pix_key']
        text = info_data['pay_template']

    if info_data['language'] == 'pt':
        issue_date_str = f"{issue_date['d']}/{issue_date['m']}/{issue_date['y']}"
        due_date_str = f"{due_date['d']}/{due_date['m']}/{due_date['y']}"
        body = replace_text(text, ['{name}', '{descr}', '{amount}', '{issue_date}', '{due_date}', '{pix}', '{condo_name}', '{payment_ref}'],
                            [name, descr, amount, issue_date_str, due_date_str, pix, condo_name, payment_id])
    elif info_data['language'] == 'en':
        issue_date_str = f"{issue_date['m']}/{issue_date['d']}/{issue_date['y']}"
        due_date_str = f"{due_date['m']}/{due_date['d']}/{due_date['y']}"
        body = replace_text(text, ['{name}', '{descr}', '{amount}', '{issue_date}', '{due_date}', '{condo_name}', '{payment_ref}'],
                            [name, descr, amount, issue_date_str, due_date_str, condo_name, payment_id])
    else:
        due_date = f"{due_date['m']}/{due_date['d']}/{due_date['y']}"
        body = replace_text(text, ['{name}', '{descr}', '{amount}', '{due_date}', '{condo_name}'], [name, descr, amount, due_date, condo_name])

    send_email_redmail(email, title, body)
    print(f"end of send_payment_notification()")

def replace_text(text, field_names, field_values):
    i = 0
    final_text = text
    for name in field_names:
        final_text = final_text.replace(name, field_values[i])
        i += 1
    return final_text

@app.route('/<tenant>/about')
def about(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    info_data = get_info_data(tenant)
    lock.release()
    return render_template("about.html", v_number=config['version']['number'], v_date=config['version']['date'],
                           user_types=staticvars.user_types, info_data=info_data)

@app.route('/<tenant>/profile')
@login_required
def profile(tenant):
    lock.acquire()

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    info_data = get_info_data(tenant)
    units = get_unit_list()
    lock.release()
    return render_template("profile.html", units=units, user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/get_system_settings')
@login_required
def get_system_settings(tenant):
    lock.acquire()
    print(f"here in get_system_settings()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    info_data = get_info_data(tenant)
    home_text = ''
    for line in info_data['home_message']['lines']:
        home_text += f"{line}\n"
    about_text = ''
    for line in info_data['about_message']['lines']:
        about_text += f"{line}\n"
    info_data['home_message']['text'] = home_text
    info_data['about_message']['text'] = about_text

    if 'pay_pix_key' not in info_data:
        info_data['pay_pix_key'] = ''

    if 'pay_title' not in info_data:
        info_data['pay_title'] = ''

    if 'pay_template' not in info_data:
        info_data['pay_template'] = ''

    lock.release()
    return json.dumps(info_data)

@app.route('/<tenant>/update_system_settings', methods=["POST"])
@login_required
def update_settings(tenant):
    lock.acquire()
    print(f"here in upload_settings()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_req = request.get_json()
    info = get_json_from_file_no_tenant(f"{INFO_FILE}")
    info['config'][tenant]['condo_name'] = json_req['request']['condo_name']
    info['config'][tenant]['tagline'] = json_req['request']['condo_tagline']
    info['config'][tenant]['condo_city'] = json_req['request']['condo_city']
    info['config'][tenant]['condo_state'] = json_req['request']['condo_state']
    info['config'][tenant]['address'] = json_req['request']['condo_address']
    info['config'][tenant]['address_number'] = json_req['request']['condo_address_number']
    info['config'][tenant]['zip'] = json_req['request']['condo_zip']
    info['config'][tenant]['home_message']['title'] = json_req['request']['home_page_title']
    info['config'][tenant]['about_message']['title'] = json_req['request']['about_page_title']
    home_text = json_req['request']['home_page_text'].split('\n')
    about_text = json_req['request']['about_page_text'].split('\n')
    lat, long = get_lat_long(f"{json_req['request']['condo_city']}, {json_req['request']['condo_state']}")
    print(f"lat {lat},  long {long}")
    info['config'][tenant]['geo']['lat'] = lat
    info['config'][tenant]['geo']['long'] = long
    info['config'][tenant]['home_message']['lines'] = [ msg for msg in home_text if len(msg.strip()) > 0]
    info['config'][tenant]['about_message']['lines'] = [ msg for msg in about_text if len(msg.strip()) > 0]
    info['config'][tenant]['pix_key'] = json_req['request']['pix_key']
    info['config'][tenant]['fine_template'] = json_req['request']['fine_template']
    info['config'][tenant]['fine_title'] = json_req['request']['fine_email_title']
    info['config'][tenant]['pay_pix_key'] = json_req['request']['pay_pix_key']
    info['config'][tenant]['pay_template'] = json_req['request']['pay_template']
    info['config'][tenant]['pay_title'] = json_req['request']['pay_email_title']
    save_json_to_file_no_tenant(f"{INFO_FILE}", info)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


#------------------------------------------------------------------------------------------
#   Announcs related routes
#------------------------------------------------------------------------------------------
@app.route('/<tenant>/announcs')
def get_announcs(tenant):
    lock.acquire()
    print(f"here in announcs()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    if aws.is_file_found(f"{tenant}/{ANNOUNCS_FILE}"):
        announcs = get_json_from_file(tenant, ANNOUNCS_FILE)['announcs']
    else:
        announcs = {}

    info_data = get_info_data(tenant)
    announcs_list = []

    for key, announc in announcs.items():
        announc['timestamp'] = get_string_from_epoch(announc['created_on'], info_data['language'])
        file_name, file_ext = os.path.splitext( announc['file_name'] )
        announc['file_ext'] = file_ext[1:] # 1 to skip the "."
        announc['key'] = key
        announcs_list.append(announc)

    # sort in descending order by date
    announcs_list.sort(key=sort_announcs_descend)

    lock.release()
    return render_template("announcs.html", announcs=announcs_list, user_types=staticvars.user_types, info_data=info_data)

def sort_announcs_descend(obj):
    return -obj['created_on'] # the "-" sign reverses the order


@app.route('/<tenant>/save_announc', methods=["POST"])
def save_announc(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    tenant = request.form['tenant']
    user_id = request.form['created_by']
    text = request.form['text']
    file_name = request.form['attach_file_name']
    if file_name:
        attach_file = request.files['attach_file'].read()
    else:
        attach_file = None

    save_announc_common(tenant, user_id, text, file_name, attach_file)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

def save_announc_common(tenant, user_id, text, file_name, attach_file):
    print(f"tenant {tenant},  created_by {user_id},  file_name: {file_name},  text: {text}")

    if aws.is_file_found(f"{tenant}/{ANNOUNCS_FILE}"):
        announcs = get_json_from_file(tenant, ANNOUNCS_FILE)
    else:
        announcs = { "announcs": {} }

    epoch = get_epoch_from_now()
    timestamp = get_string_from_epoch_format(epoch, '%Y%m%d')
    seq = 0
    while True:
        key = f"{timestamp}_{seq}"
        if key not in announcs['announcs']:
            break
        else:
            seq += 1

    if file_name:
        _, file_ext = os.path.splitext( file_name )
        mod_file_name = f"{key}{file_ext}"
        print(f"mod_file_name: {mod_file_name}")
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/announcs/{mod_file_name}", attach_file)
    else:
        mod_file_name = ''

    announcs['announcs'][key] = {
        "created_on": epoch,
        "created_by": user_id,
        "file_name": mod_file_name,
        "text": text
    }

    # save the JSON file
    resp = save_json_to_file(tenant, ANNOUNCS_FILE, announcs)
    print(f"aws resp: {resp}")


@app.route('/<tenant>/delete_announc', methods=["POST"])
@login_required
def delete_announc(tenant):
    lock.acquire()
    print(f"here in delete_announc()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_obj = request.get_json()
    prefix = "announc"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    announc_id = json_obj[prefix]['announc_id']

    print(f"tenant: {tenant},  user_id: {user_id},  announc_id: {announc_id}")

    if aws.is_file_found(f"{tenant}/{ANNOUNCS_FILE}"):
        announcs_content = get_json_from_file(tenant, ANNOUNCS_FILE)
        if 'announcs' not in announcs_content:
            return_obj = json.dumps({'response': {'status': 'success'}})
            lock.release()
            return return_obj
    else:
        return_obj = json.dumps({'response': {'status': 'file_not_found'}})
        lock.release()
        return return_obj

    if announc_id in announcs_content['announcs']:
        file_name = announcs_content['announcs'][announc_id]['file_name']
        del announcs_content['announcs'][announc_id]
        print(f"announcement deleted. file_name: {file_name}")
    else:
        return_obj = json.dumps({'response': {'status': 'announc_not_found'}})
        lock.release()
        return return_obj

    # first update the ANNOUNCS_FILE
    save_json_to_file(tenant, ANNOUNCS_FILE, announcs_content)

    # now, delete the attachment file, if any
    if file_name:
        aws.delete_object(f"{tenant}/uploadedfiles/unprotected/announcs/{file_name}")
        print(f"attach file deleted")

    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/email_announc', methods=["POST"])
@login_required
def email_announc(tenant):
    lock.acquire()
    print(f"here in email_announc()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_obj = request.get_json()
    prefix = "announc"
    tenant_json = json_obj[prefix]['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    user_id = json_obj[prefix]['user_id']
    announc_id = json_obj[prefix]['announc_id']

    print(f"tenant: {tenant},  user_id: {user_id},  announc_id: {announc_id}")

    if aws.is_file_found(f"{tenant}/{ANNOUNCS_FILE}"):
        announcs_content = get_json_from_file(tenant, ANNOUNCS_FILE)
        if 'announcs' not in announcs_content:
            return_obj = json.dumps({'response': {'status': 'error'}})
            lock.release()
            return return_obj
    else:
        return_obj = json.dumps({'response': {'status': 'file_not_found'}})
        lock.release()
        return return_obj

    if announc_id in announcs_content['announcs']:
        text = announcs_content['announcs'][announc_id]['text']
    else:
        return_obj = json.dumps({'response': {'status': 'announc_not_found'}})
        lock.release()
        return return_obj

    info_data = get_info_data(tenant)

    if info_data['language'] == 'pt':
        subject = "Um novo anúncio acaba de ser postado"
        body = f"""Prezados Moradores, um novo anúncio acaba de ser postado. Por favor veja a seção de Anúncios do nosso website.
\nResumo do anúncio:
{text}
        """
    else:
        subject = "A new Announcement has been posted"
        body = f"""Dear residents, a new announcement has been posted. Please see the Announcement section of the website.
\nSummary of the announcement:
{text}
        """

    print(f"subject: {subject}, body: {body}")
    send_email_to_all(tenant, subject, body)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/getannouncs')
def get_announc_list(tenant):
    lock.acquire()
    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    announc_list = []
    string_content = get_json_from_file(tenant, ANNOUNCS_FILE)
    alist = string_content.split('\n') # create a list divided by the new-line char
    for line in alist:
        if len(line.strip()): # add only lines that are not blank
            announc_list.append(line)
    json_obj = {'announcs':announc_list} # announc_list contains no blank line as item
    lock.release()
    return json.dumps(json_obj)


#------------------------------------------------------------------------------------------
#   Docs related routes
#------------------------------------------------------------------------------------------
@app.route('/<tenant>/docs')
def get_docs(tenant):
    print(f"here in get_docs: tenant: {tenant}")
    lock.acquire()

    page, error_code = check_security(tenant)
    if error_code == TENANT_NOT_FOUND_CODE:
        lock.release()
        return page

    open_docs = get_doc_files_cache(tenant, f"{UNPROTECTED_FOLDER}/opendocs/files", '')
    info_data = get_info_data(tenant)

    if error_code == USER_NOT_AUTHENTICATED_CODE:
        lock.release()
        return render_template("docs-open.html", opendocs=open_docs, info_data=info_data)

    # f"{PROTECTED_FOLDER}/docs/financial/{doc_year}"
    # f"{PROTECTED_FOLDER}/docs/financial/{year}"

    # here user is authenticated, aka logged in
    start_year = datetime.now().year - 4
    fin_docs = {}
    for year in range(10):
        year = start_year + year
        docs = get_doc_files_cache(tenant, f"{PROTECTED_FOLDER}/docs/financial/{year}", f"Fin-{year}")
        if len(docs) > 0:
            fin_docs[year] = docs

    bylaws = get_doc_files_cache(tenant, f"{PROTECTED_FOLDER}/docs/bylaws", '')
    other_docs = get_doc_files_cache(tenant, f"{PROTECTED_FOLDER}/docs/other", '')
    links = get_json_from_file(tenant, LINKS_FILE)
    bylaws = [] if bylaws is None else bylaws
    other_docs = [] if other_docs is None else other_docs
    open_docs = [] if open_docs is None else open_docs
    links = [] if links is None else links['links'].items()
    lock.release()
    return render_template("docs.html", bylaws=bylaws, otherdocs=other_docs, opendocs=open_docs,
        findocs=fin_docs.items(), links=links,
        user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/delete_fin_doc_group', methods=["POST"])
@login_required
def delete_fin_doc_group(tenant):
    lock.acquire()
    print(f"here in delete_fin_doc_group()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_req = request.get_json()
    year = json_req['request']['year']
    partial_path = f"{PROTECTED_FOLDER}/docs/financial/{year}"
    docs = get_doc_files_cache(tenant, partial_path, f"Fin-{year}")
    status = 'success'

    for doc in docs:
        filepath = f"{tenant}/{PROTECTED_FOLDER}/docs/financial/{year}/{doc}"
        resp = aws.delete_object(f"{filepath}")
        if resp:
            print(f"file deleted: {filepath}")
            continue
        else:
            status = 'failure'
            print(f"deletion failed: {filepath}")
            break

    key = f"{tenant}-{partial_path}"
    print(f"key to be deleted: {key}")
    if key in doc_files_cache:
        print(f"key found, will be deleted: {key}")
        invalidate_doc_files_cache(tenant, partial_path)  # to force an aws read next time

    return_obj = { 'response': {'status': status} }
    lock.release()
    return json.dumps(return_obj)


@app.route('/users')
@login_required
def get_users():
    if current_user.is_authenticated and current_user.type == staticvars.USER_TYPE_ADMIN:
        all_users = users_repository.get_users()
    else:
        all_users = []
    return render_template("users.html", users=all_users)


@app.route('/residents')
def get_residents():
    #all_users = []
    #for user in users_repository.get_users():
    #    user = users_repository.get_user_by_unit(key)
    #    all_users.append(user)
    return render_template("residents.html", users=users_repository.get_users())


@app.route('/<tenant>/getresidents', methods=['POST'])
def get_residents_json(tenant):
    lock.acquire()
    print(f"in get_residents_json(): tenant {tenant}")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    resident_list = []

    for user in users_repository.get_users(tenant):
#        user = users_repository.get_user_by_unit(key)
        if current_user.is_authenticated and current_user.type == staticvars.USER_TYPE_ADMIN:
            passw = user.password
        else:
            passw = ''
        #log(f"logged-in user: {current_user.userid}  user is authenticated: {current_user.is_authenticated}   user type: {current_user.type}")
        resident_list.append( {'unit':user.unit,
                               'userid':user.userid,
                               'usertype':user.type,
                               'password':passw,
                               'name':user.name,
                               'email':user.email,
                               'startdt':user.startdt,
                               'phone':user.phone,
                               'type':user.type,
                               'ownername': user.ownername,
                               'owneremail': user.owneremail,
                               'ownerphone': user.ownerphone,
                               'owneraddress': user.owneraddress,
                               'isrental': user.isrental,
                               'occupants': user.occupants
                               } )

    resident_list.sort(key=sort_criteria)
    json_obj = {'residents':resident_list}
    lock.release()
    return json.dumps(json_obj)


@app.route('/getloggedinuser')
def get_loggedin_user():
    resident = {'userid':current_user.userid, 'unit':current_user.unit}
    return_obj = {'status': 'success', 'resident': resident}
    return json.dumps({'response': return_obj})


@app.route('/<tenant>/pics')
def pics(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    info_data = get_info_data(tenant)
    pictures = get_files(tenant, f"{UNPROTECTED_FOLDER}/pics", '')

    if not aws.is_file_found(f"{tenant}/{EVENT_PICS_FILE}"):
        lock.release()
        return render_template("pics.html", pics=pictures, events=None, user_types=staticvars.user_types, info_data=get_info_data(tenant))

    events = get_json_from_file(tenant, EVENT_PICS_FILE)

    # convert from epoch to string date format
    for event_key, event_data in events['event_pictures'].items():
        event_data['date'] = get_string_from_epoch(event_data['date'], info_data['language'])

    lock.release()
    return render_template("pics.html", pics=pictures, events=events['event_pictures'].items(), user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/logout', methods=['GET'])
def logout(tenant):
    print(f"logout(): session: {session}")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    if not current_user.is_authenticated:
        return redirect(f"/{tenant}/home")

    # from here on down we know that an user is logged in
    print(f"user to be logged out: {current_user.userid}")

    current_user.authenticated = False
    userid = current_user.userid  # we need to save the userid BEFORE invoking logout_user()
    logout_user()
    session['tenant'] = None
    return render_template("logout.html", loggedout_user=userid, info_data=get_info_data(tenant))

'''
  These are POST request routes
'''
@app.route('/<tenant>/delete_file', methods=['POST'])
def delete_file(tenant):
    lock.acquire()
    print(f"here in delete_file()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    file_obj = request.get_json()
    req_tenant = file_obj['request']['tenant']
    file_path = file_obj['request']['filepath']
    protected = file_obj['request']['protected']

    file_path_del = f"{tenant}/{PROTECTED_FOLDER}/{file_path}" if protected == 'yes' else f"{tenant}/{UNPROTECTED_FOLDER}/{file_path}"
    print(f"file to be deleted: {file_path_del}")
    partial_path = f"{PROTECTED_FOLDER}/{file_path}" if protected == 'yes' else f"{UNPROTECTED_FOLDER}/{file_path}"
    partial_path = os.path.dirname(partial_path)

    if not aws.is_file_found(file_path_del):
        return_obj = {'status': 'success'}
        lock.release()
        return json.dumps(return_obj)

    resp = aws.delete_object(f"{file_path_del}")
    if partial_path:
        key = f"{tenant}-{partial_path}"
        print(f"key to be deleted: {key}")
        if key in doc_files_cache:
            print(f"key found, will be deleted: {key}")
            invalidate_doc_files_cache(tenant, partial_path)  # to force an aws read next time

#    status = 'success' if resp == 'success' else 'failure'
    status = 'success'
    return_obj = {'status': status}
    lock.release()
    return json.dumps(return_obj)

#------------------------------------------------------------
# will send email to a resident
#------------------------------------------------------------
@app.route('/sendsinglemail', methods=['POST'])
def send_single_email():
    mailObj = request.get_json()
    emailto = mailObj['request']['emailto']
    subject = mailObj['request']['subject']
    body = mailObj['request']['body']
    if len(emailto.strip()):
        send_email_relay_host(emailto, subject, body)
    return_obj = json.dumps({'response': {'status': 'success'}})
    return return_obj


@app.route('/send_contact_mail', methods=['GET' , 'POST'])
def send_contact_email():
    print(f"here in send_contact_email(), method {request.method}")
    print(f"form {request.form}")
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    body = f"name: {name} \nemail: {email} \nphone: {phone} \nmessage: {request.form['message']}"
    print(f"name: {name},  emailto {email},  phone {phone},  body {body}")
    #send_email_local(CONTACT_TARGET_EMAIL, 'Message from CondoSpace contact form', body, 'localhost', 25)
    send_email_redmail(CONTACT_TARGET_EMAIL, 'Message from CondoSpace contact form', body)
    print(f"end of send_contact_email()")
    return redirect(url_for('home'))


def print_process(route, unit, newline=True):
    #nl = "\n" if newline else ""
    #print(f"{route}, pid {os.getpid()}, tenant {get_tenant()}, unit {unit} {nl}")
    pass

@app.route('/<tenant>/getresident', methods=["POST"])
def get_resident_json(tenant):
    lock.acquire()
    print(f"in get_resident_json(): tenant: {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    tenant_json = json_obj['request']['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    #print_process("/getresident start", json_obj['request']['id'], False)
    load_users(tenant)
    if json_obj['request']['type'] == 'user':
        print(f"user id to retrieve: {json_obj['request']['id']}")
        user = users_repository.get_user_by_userid(tenant, json_obj['request']['id'])
    else:
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    if user is None:
        return_obj = json.dumps({'response': {'status': 'not_found'}})
        lock.release()
        return return_obj

    passw = user.password

    resident = {
        'unit':user.unit,
        'userid':user.userid,
        'password':passw,
        'name':user.name,
        'email':user.email,
        'startdt':user.startdt,
        'phone':user.phone,
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

    return_obj = json.dumps({'response': {'status': 'success', 'pid': os.getpid(), 'resident':resident}})
    #print_process("/getresident finis", json_obj['request']['id'])
    lock.release()
    return return_obj

@app.route('/<tenant>/saveresident', methods=["POST"])
def save_resident_json(tenant):
    lock.acquire()
    print(f"in save_resident_json(): tenant {tenant}")
    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    tenant_json = json_obj['resident']['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    load_users(tenant)
    db_user = users_repository.get_user_by_userid(tenant, json_obj['resident']['userid'])

    if db_user is None:
        #id = users_repository.next_index()
        print(f"id :  {id}")
        user = User(
            f"{tenant}-{json_obj['resident']['userid']}",
            users_repository.get_last_unit(tenant) + 1,
            tenant,
            json_obj['resident']['userid'],
            json_obj['resident']['password'],
            json_obj['resident']['name'],
            json_obj['resident']['email'],
            json_obj['resident']['startdt'],
            json_obj['resident']['phone'],
            json_obj['resident']['type'],
            json_obj['resident']['ownername'],
            json_obj['resident']['owneremail'],
            json_obj['resident']['ownerphone'],
            json_obj['resident']['owneraddress'],
            json_obj['resident']['isrental'],
            json_obj['resident']['emerg_name'],
            json_obj['resident']['emerg_email'],
            json_obj['resident']['emerg_phone'],
            json_obj['resident']['emerg_has_key'],
            json_obj['resident']['occupants'],
            json_obj['resident']['oxygen_equipment'],
            json_obj['resident']['limited_mobility'],
            json_obj['resident']['routine_visits'],
            json_obj['resident']['has_pet'],
            json_obj['resident']['bike_count'],
            json_obj['resident']['insurance_carrier'],
            json_obj['resident']['valve_type'],
            json_obj['resident']['no_vehicles'],
            json_obj['resident']['vehicles'],
            '',
            json_obj['resident']['notes']
        )
    else:
        db_user.name = json_obj['resident']['name']
        db_user.email = json_obj['resident']['email']
        db_user.startdt = json_obj['resident']['startdt']
        db_user.phone = json_obj['resident']['phone']
        if 'password' in json_obj['resident']:
            db_user.password = json_obj['resident']['password']
        if 'type' in json_obj['resident']:
            db_user.type = json_obj['resident']['type']
        db_user.ownername = json_obj['resident']['ownername']
        db_user.owneremail = json_obj['resident']['owneremail']
        db_user.ownerphone = json_obj['resident']['ownerphone']
        db_user.owneraddress = json_obj['resident']['owneraddress']
        db_user.isrental = json_obj['resident']['isrental']
        db_user.occupants = json_obj['resident']['occupants']
        db_user.emerg_name = json_obj['resident']['emerg_name']
        db_user.emerg_email = json_obj['resident']['emerg_email']
        db_user.emerg_phone = json_obj['resident']['emerg_phone']
        db_user.emerg_has_key = json_obj['resident']['emerg_has_key']
        db_user.occupants = json_obj['resident']['occupants']
        db_user.oxygen_equipment = json_obj['resident']['oxygen_equipment']
        db_user.limited_mobility = json_obj['resident']['limited_mobility']
        db_user.routine_visits = json_obj['resident']['routine_visits']
        db_user.has_pet = json_obj['resident']['has_pet']
        db_user.bike_count = json_obj['resident']['bike_count']
        db_user.insurance_carrier = json_obj['resident']['insurance_carrier']
        db_user.valve_type = json_obj['resident']['valve_type']
        db_user.no_vehicles = json_obj['resident']['no_vehicles']
        db_user.vehicles = json_obj['resident']['vehicles']
        db_user.last_update_date = json_obj['resident']['last_update_date']
        db_user.notes = json_obj['resident']['notes']
        user = db_user

    # this assign the user object on the hash (dict), where the unit is key, user is value
    #users_repository.save_user(user)

    # save the entire list of users to a file
    #users_repository.save_users(get_tenant())

    users_repository.save_user_and_persist(tenant, user)
    return_obj = json.dumps({'response': {'status': 'success', 'pid': os.getpid()}})
    #print_process("/saveresident finis", json_obj['resident']['unit'])
    lock.release()
    return return_obj


@app.route('/deleteresident', methods=["POST"])
def delete_resident_json():
    lock.acquire()
    json_obj = request.get_json()
    tenant = json_obj['resident']['tenant']
    load_users(tenant)
    user = users_repository.get_user_by_userid(tenant, json_obj['resident']['value'])
    status = 'success' if users_repository.delete_user(tenant, user) == True else 'error'
    users_repository.persist_users(tenant)
    return_obj = json.dumps({'response': {'status': status}})
    lock.release()
    return return_obj


@app.route('/saveresidentpartial', methods=["POST"])
def save_resident_partial():
    lock.acquire()
    json_obj = request.get_json()
    db_user = users_repository.get_user_by_unit(json_obj['resident']['unit'])

    if db_user is None:
        return_obj = {'status': 'failure'}
        lock.release()
        return json.dumps({'response': return_obj})
    else:
        db_user.userid = json_obj['resident']['userid']
        db_user.password = json_obj['resident']['password']
        db_user.name = json_obj['resident']['name']
        db_user.email = json_obj['resident']['email']
        db_user.phone = json_obj['resident']['phone']
        db_user.startdt = json_obj['resident']['startdt']
        db_user.type = json_obj['resident']['type']
        db_user.ownername = json_obj['resident']['owner_name']
        db_user.owneremail = json_obj['resident']['owner_email']
        db_user.ownerphone = json_obj['resident']['owner_phone']
        db_user.owneraddress = json_obj['resident']['owner_address']
        db_user.emerg_name = json_obj['resident']['emerg_name']
        db_user.emerg_email = json_obj['resident']['emerg_email']
        db_user.emerg_phone = json_obj['resident']['emerg_phone']
        db_user.emerg_has_key = json_obj['resident']['emerg_has_key']
        db_user.occupants = json_obj['resident']['occupants']
        user = db_user

    # this assigns the user object on the hash (dict), where the unit is key, user is value
    #users_repository.save_user(user)

    # save the entire list of users to a file
    #users_repository.save_users(get_tenant())
    
    users_repository.save_user_and_persist(get_tenant(), user)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

@app.route('/<tenant>/changepassword', methods=["POST"])
def change_password(tenant):
    lock.acquire()
    print(f"here in change_password(): tenant {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    json_obj = request.get_json()
    tenant_json = json_obj['resident']['tenant']

    if tenant != tenant_json:
        return_obj = json.dumps({'response': {'status': 'error', 'pid': os.getpid()}})
        lock.release()
        return return_obj

    print(f"this is the entire request obj: {json_obj}")

    user_id = json_obj['resident']['user_id']
    db_user = users_repository.get_user_by_userid(tenant, user_id)

    if db_user is None:
        return_obj = json.dumps({'response': {'status': 'error', 'message': f"User {user_id} not found"}})
        lock.release()
        return return_obj

    db_user.password = json_obj['resident']['password']
    users_repository.save_user_and_persist(tenant, db_user)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/upload_link', methods=["POST"])
@login_required
def upload_link(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    json_req = request.get_json()
    links = get_json_from_file(tenant, LINKS_FILE)
    if links is None:
        links_dict = { "links": {} }
    else:
        links_dict = { "links": links['links']}
    links_dict['links'][json_req['request']['link_descr']] = { 'url': json_req['request']['link_url'] }
    print(f"new links are: {links_dict}")
    save_json_to_file(tenant, LINKS_FILE, links_dict)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/resetpassword', methods=["POST"])
@login_required
def reset_password():
    lock.acquire()
    user_obj = request.get_json()
    unit_id = int(user_obj['unit_id'])
    recipient_email = user_obj['recipient_email']
    db_user = users_repository.get_user_by_unit(unit_id)
    new_password = generate_password(db_user.userid)
    #print(f"new password: {new_password}")
    db_user.password = new_password

    # save this user in an internal structure
    #users_repository.save_user(db_user)

    # save the entire list of users to a file
    #users_repository.save_users(get_tenant())

    users_repository.save_user_and_persist(get_tenant(), db_user)
    
    # send email
    email_body = f"Dear resident, your login info has changed to this below:\n\nUser Id: {db_user.userid}\nPassword: {new_password}\n\nWebsite administrator."
    send_email_relay_host(db_user.email, 'Your condominium login info was reset', email_body)

    if len(recipient_email) > 0:
        send_email_relay_host(recipient_email, 'Your condominium login info was reset', email_body)

    return_obj = json.dumps({'response': {'status': 'success', 'owner_email': db_user.email, 'authorized_email': recipient_email}})
    lock.release()
    return return_obj


@app.route('/changeuserid', methods=["POST"])
def change_userid():
    lock.acquire()
    json_obj = request.get_json()
    db_user = users_repository.get_user_by_unit(json_obj['resident']['unit'])
    db_user.userid = json_obj['resident']['userid']
    users_repository.save_user_and_persist(get_tenant(), db_user)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


#-----------------------------------------------------------------------------------------------------
#     Listing routines
#-----------------------------------------------------------------------------------------------------
@app.route('/<tenant>/listing/<unit>/<listing_id>')
def get_one_listing(tenant, unit, listing_id):
    lock.acquire()
    print(f"get_one_listing()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    listings = get_json_from_file(tenant, LISTINGS_FILE)
    info_data = get_info_data(tenant)
    alisting = None
    pictures = None

    if unit in listings['listings']:
        alisting = listings['listings'][unit]['items'][listing_id]
        alisting['listing_id'] = listing_id
        alisting['date'] = get_string_from_epoch(alisting['date'], info_data['language'])
        alisting['price'] = format_decimal(alisting['price'])
        pictures = get_files(tenant, f"{UNPROTECTED_FOLDER}/listings/{unit}/{listing_id}/pics", '')

    lock.release()
    return render_template("alisting.html", unit=unit, listing=alisting, pics=pictures, user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/upload_listing', methods=['POST'])
def upload_listing(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    upload_files = request.files.getlist("file_array")
    #upload_file_sizes = request.files.getlist("file_size_array")
    #print(f"unit: {request.form['unit']}, title: {request.form['title']}, contact: {request.form['contact']}, price: {request.form['price']}")
    if len(upload_files) == 0:
        print("no files were received")
        return_obj = json.dumps({'response': {'status': 'success'}})
        return return_obj

    img_bytes = None
    cover_found = False
    cover_name = ''
    user_id = request.form["unit"]

    # this is to find the cover file name, if any
    for file in upload_files:
        if not is_valid_graphic_file(file.filename):
            continue
        if file.filename.startswith("cover"):
            cover_found = True
            cover_name = file.filename

    if cover_found is False:
        upload_files[0].stream.seek(0)
        img_bytes = upload_files[0].read()
        cover_image = Image.open(BytesIO(img_bytes))
        img_format = cover_image.format
        w, h = cover_image.size
        if w > h:
            nw = 200
            p = 200 / w
            nh = int(h * p)
        else:
            nh = 150
            p = 150 / h
            nw = int(w * p)
        resized_img = cover_image.resize((nw, nh), Image.Resampling.LANCZOS)
        img_bytes = image_to_byte_array(resized_img, img_format)
        cover_name = "cover.jpg" if img_format == 'JPEG' else "cover.png"
        upload_files[0].stream.seek(0)

    new_listing = { "title": request.form["title"], "email": request.form["email"], "phone": request.form["phone"],
                    "price": int(request.form["price"]), "cover_file": cover_name, "date": get_epoch_from_now() }

    # read the LISTINGS_FILE to add an additional condo to it
    if aws.is_file_found(f"{get_tenant()}/{LISTINGS_FILE}"):
        listings = get_json_from_file(tenant, LISTINGS_FILE)

        # find the last listing_id for the user
        if user_id in listings['listings']:
            listing_id = 0
            for id, value in listings['listings'][user_id]['items'].items():
                id = int(id)
                listing_id = id if id > listing_id else listing_id
            listing_id += 1
            listings['listings'][user_id]['items'][listing_id] = new_listing
        else:
            listing_id = 0
            listings['listings'][user_id] = { 'items':  { listing_id: new_listing } }
    else:
        listing_id = 0
        listings = { 'listings': {
            user_id: { "items": { listing_id: new_listing } } } }

    save_json_to_file(tenant, LISTINGS_FILE, listings)

    # here we know the listing_id, let's upload the files
    for file in upload_files:
        if not is_valid_graphic_file(file.filename):
            continue
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/listings/{user_id}/{listing_id}/pics/{file.filename}", file.read())

    if cover_found is False and img_bytes is not None:
        print(f"there is no cover, uploading the one we created: {cover_name}")
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/listings/{user_id}/{listing_id}/pics/{cover_name}", img_bytes)
    else:
        print(f"problem processing the cover file")

    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/listings')
def get_listings(tenant):
    lock.acquire()
    print(f"get_listings()")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    if not aws.is_file_found(f"{tenant}/{LISTINGS_FILE}"):
        lock.release()
        return render_template("listings.html", units=get_unit_list(), listings=None,
                               user_types=staticvars.user_types, info_data=get_info_data(tenant))

    listings = get_json_from_file(tenant, LISTINGS_FILE)
    info_data = get_info_data(tenant)
    listings_arr = []

    for key, value_a in listings['listings'].items():
        #print(f"key: {key}     items: {value_a}")
        for listing_id, value_c in value_a['items'].items():
            value_c['price'] = format_decimal(format(value_c['price']))
            value_c['date'] = get_string_from_epoch(value_c['date'], info_data['language'])
            listings_arr.append( {'user_id': key, 'listing_id': listing_id, 'title': value_c['title'], 'email': value_c['email'], 'phone': value_c['phone'],
                                  'price': value_c['price'], 'cover_file': value_c['cover_file'], 'date': value_c['date']} )

    lock.release()
    return render_template("listings.html",
                           units=get_unit_list(include_adm=False), listings=listings_arr,
                           user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/delete_listing', methods=['POST'])
def delete_listing(tenant):
    lock.acquire()
    print(f"here in delete_listing(): {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    user_id = request.get_json()['request']['user_id']
    listing_id = request.get_json()['request']['listing_id']
    pictures = aws.get_file_list_folder(tenant, f"{UNPROTECTED_FOLDER}/listings/{user_id}/{listing_id}/pics")
    for pic_name in pictures:
        pic_name = pic_name[ len(BUCKET_PREFIX + "/"): ]
        aws.delete_object(pic_name)

    listings = get_json_from_file(tenant, LISTINGS_FILE)
    del listings['listings'][user_id]['items'][listing_id]
    save_json_to_file(tenant, LISTINGS_FILE, listings)

    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


#-----------------------------------------------------------------------------------------------------
#     Picture event routines
#-----------------------------------------------------------------------------------------------------
@app.route('/<tenant>/event/<title>')
def get_event_pics(tenant, title):
    lock.acquire()
    print(f"in get_event_pics(): tenant: {tenant}")
    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    pictures = get_files(tenant, f"{UNPROTECTED_FOLDER}/eventpics/{title}/pics", '')
    events = get_json_from_file(tenant, EVENT_PICS_FILE)
    info_data = get_info_data(tenant)
    if title not in events['event_pictures']:
        event = None
        pictures = None
    else:
        event = events['event_pictures'][title]
        event['date'] = get_string_from_epoch(event['date'], info_data['language'])
        print(f"info do evento: {event}")
    lock.release()
    return render_template("event.html", title=title, event=event, pics=pictures, user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/upload_event_pics', methods=['POST'])
def upload_event_pics(tenant):
    lock.acquire()
    print(f"here in upload_event_pics(): tenant {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    upload_files = request.files.getlist("file_array")
    #upload_file_sizes = request.files.getlist("file_size_array")
    #print(f"here in upload_event_pics(): {len(upload_files)}, title: {request.form['title']}, date: {request.form['date']}")

    # upload the files first
    folder_name = request.form['title'].strip().lower().replace(" ", "_")
    cover_found = False
    cover_name = ''

    # upload all pictures to aws
    for file in upload_files:
        if file.filename.startswith("cover"):
            cover_found = True
            cover_name = file.filename
            file.stream.seek(0)
            img_bytes = file.read()
            (_, w, h) = get_format_and_size(img_bytes)
            # this logic takes into account whether the image is horizontal
            if w > h:
                if w > COVER_PREF_WIDTH:
                    nw = COVER_PREF_WIDTH  # image is horizontal, let's fix the width
                    p = COVER_PREF_WIDTH / w
                    nh = int(h*p)
                else:
                    nw = COVER_PREF_WIDTH
                    nh = COVER_PREF_HEIGHT
            else:
                if h > COVER_PREF_HEIGHT:
                    nh = COVER_PREF_HEIGHT # image is vertical, let's fix the height
                    p = COVER_PREF_HEIGHT / h
                    nw = int(w*p)
                else:
                    nw = COVER_PREF_WIDTH
                    nh = COVER_PREF_HEIGHT
            img_format, new_img_bytes = reduce_image_enh(img_bytes, nw, nh)
            cover_name = "cover.jpg" if img_format == 'JPEG' else "cover.png"
            aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/eventpics/{folder_name}/pics/{cover_name}", new_img_bytes)
        else:
            aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/eventpics/{folder_name}/pics/{file.filename}", file.read())

    if cover_found is False:
        upload_files[0].stream.seek(0)
        img_bytes = upload_files[0].read()
        cover_image = Image.open(BytesIO(img_bytes))
        w, h = cover_image.size
        # this logic takes into account whether or not the image is horizontal
        if w > h:
            nw = COVER_PREF_WIDTH  # image is horizontal, let's fix the width
            p = COVER_PREF_WIDTH / w
            nh = int(h*p)
        else:
            nh = COVER_PREF_HEIGHT # image is vertical, let's fix the height
            p = COVER_PREF_HEIGHT / h
            nw = int(w*p)
        img_format, new_img_bytes = reduce_image_enh(img_bytes, nw, nh)
        cover_name = "cover.jpg" if img_format == 'JPEG' else "cover.png"
        aws.upload_binary_obj(f"{tenant}/{UNPROTECTED_FOLDER}/eventpics/{folder_name}/pics/{cover_name}", new_img_bytes)

    event_date = f"{request.form['event_y']}-{request.form['event_m']}-{request.form['event_d']}"
    print(f"event_date: {event_date}")
    event_date_epoch = get_epoch_from_string(event_date)
    print(f"event_date epoch: {event_date_epoch}")

    if aws.is_file_found(f"{tenant}/{EVENT_PICS_FILE}"):
        event_pics = get_json_from_file(tenant, EVENT_PICS_FILE)
        new_event = {'title': f'{request.form["title"]}', 'date': event_date_epoch, 'cover_file': f'{cover_name}' }
        event_pics['event_pictures'][folder_name] = new_event
    else:
        new_event = {'title': f'{request.form["title"]}', 'date': event_date_epoch, 'cover_file': f'{cover_name}' }
        # new_event_dict = {folder_name: new_event}
        event_pics = {"event_pictures": { f"{folder_name}": new_event } }

    # now we upload/update the json file itself with the new content
    save_json_to_file(tenant, EVENT_PICS_FILE, event_pics)

    # prepare response
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/delete_event_pics', methods=['POST'])
def delete_event_pics(tenant):
    lock.acquire()
    print(f"here in delete_event_pics(): {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        print(f"error in delete_event_pics(): error {check_code}")
        lock.release()
        return page

    title = request.get_json()['request']['title']
    print(f"title :  {title}")
    pictures = aws.get_file_list_folder(tenant, f"{UNPROTECTED_FOLDER}/eventpics/{title}/pics")
    for pic_name in pictures:
        aws.delete_object(pic_name[10:])

    #aws.delete_object(f"{get_tenant()}/{UNPROTECTED_FOLDER}/listings/{unit}/pics")
    #aws.delete_object(f"{get_tenant()}/{UNPROTECTED_FOLDER}/listings/{unit}")

    events = get_json_from_file(tenant, EVENT_PICS_FILE)
    events['event_pictures'].pop(title, None)
    save_json_to_file(tenant, EVENT_PICS_FILE, events)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/<tenant>/delete_link', methods=['POST'])
def delete_link(tenant):
    lock.acquire()

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    descr = request.get_json()['request']['link_descr']
    print(f"tenant: {tenant}    link to be deleted: {descr}")
    links = get_json_from_file(tenant, LINKS_FILE)
    links['links'].pop(descr, None)
    save_json_to_file(tenant, LINKS_FILE, links)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/upload_event', methods=['POST'])
def upload_event():
    print("here in upload_event()")
    upload_files = request.files.getlist("file_array")
    upload_file_sizes = request.files.getlist("file_size_array")
    print(f"title: {request.form['title']}")
    if len(upload_files) == 0:
        print("no files were received")
    else:
        for file in upload_files:
            print(f'file name: {file.filename}')

    tenant = get_tenant()
    pictures = get_files(tenant, f"{UNPROTECTED_FOLDER}/pics", '')
    return render_template("pics.html", pics=pictures, info_data=get_info_data(tenant))


@app.route('/<tenant>/upload_financial', methods=['GET' , 'POST'])
@login_required
def upload_financial(tenant):
    lock.acquire()
    print(f"here in upload_financial(): {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    uploaded_file = request.files['file']
    doc_year = request.form['year']
    doc_month = request.form['month']
    file_size = request.form['filesize']
    partial_path = f"{PROTECTED_FOLDER}/docs/financial/{doc_year}"
    fullpath = f"{partial_path}/Fin-{doc_year}-{doc_month}.pdf"
    aws.upload_binary_obj(f"{tenant}/{fullpath}", uploaded_file.read())
    invalidate_doc_files_cache(tenant, partial_path)
    lock.release()
    return redirect(f"/{tenant}/docs")


@app.route('/<tenant>/upload', methods=['GET' , 'POST'])
@login_required
def upload(tenant):
    lock.acquire()
    print(f"here in upload(): {tenant}")

    page, check_code = check_security(tenant)
    if check_code != SECURITY_SUCCESS_CODE:
        lock.release()
        return page

    info_data = get_info_data(tenant)

    if request.method == 'POST':
        uploaded_file = request.files['file']
        uploaded_convname = request.form['convname']
        filename = secure_filename(uploaded_file.filename)
        filename = filename.replace('_', '-')
        filename = filename.replace(' ', '-')
        invalidate_cache = False

        if uploaded_convname == 'pubfile':
            partial_path = f"{UNPROTECTED_FOLDER}/opendocs/files"
            invalidate_cache = True
        elif uploaded_convname == 'bylaws':
            partial_path = f"{PROTECTED_FOLDER}/docs/bylaws"
            invalidate_cache = True
        elif uploaded_convname == 'otherdoc':
            partial_path = f"{PROTECTED_FOLDER}/docs/other"
            invalidate_cache = True
        elif uploaded_convname == 'picture':
            partial_path = f"{UNPROTECTED_FOLDER}/pics"
        elif uploaded_convname == 'logopic':
            partial_path = ''
        elif uploaded_convname == 'homepic':
            partial_path = ''
        else:
            print(f"upload(): No file uploaded. Unexpected file type: {uploaded_convname}")
            lock.release()
            return render_template("upload.html", user_types=staticvars.user_types, info_data=info_data)

        uploaded_file.stream.seek(0)

        if uploaded_convname == 'logopic':
            img_bytes = uploaded_file.read()
            img_format, new_img_bytes = reduce_image_enh(img_bytes, COVER_PREF_WIDTH, COVER_PREF_HEIGHT)
            logo_name = "logo.jpg" if img_format == 'JPEG' else "logo.png"
            fullpath = f"{UNPROTECTED_FOLDER}/branding/{logo_name}"
            aws.upload_binary_obj(f"{tenant}/{fullpath}", new_img_bytes)
        elif uploaded_convname == 'homepic':
            fullpath = f"{UNPROTECTED_FOLDER}/branding/home.jpg"
            aws.upload_binary_obj(f"{tenant}/{fullpath}", uploaded_file.read())
            info_data['default_home_pic'] = False
            info_obj = get_json_from_file_no_tenant(f"{INFO_FILE}")
            info_obj['config'][tenant] = info_data
            save_json_to_file_no_tenant(INFO_FILE, info_obj)
        else:
            fullpath = f"{partial_path}/{filename}"
            aws.upload_binary_obj(f"{tenant}/{fullpath}", uploaded_file.read())
            print(f"just uploaded this file: {tenant}/{fullpath}")

        if invalidate_cache:
            print(f"upload(): prior to call invalidate_do_files_cache()")
            invalidate_doc_files_cache(tenant, partial_path)

        lock.release()
        return render_template("upload.html", user_types=staticvars.user_types, info_data=info_data)
    else:
        info_data = get_info_data(tenant)
        lock.release()
        return render_template("upload.html", user_types=staticvars.user_types, info_data=info_data)


@app.route('/<tenant>/generatepdf', methods=['GET'])
def gen_pdf(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    def sort_residents(resident):
        return resident.get_unit()

    info_data = get_info_data(tenant)
    title = info_data[CONDO_NAME_STRING]
    pdf = PDF(title)
    pdf.set_title(title)
    pdf.set_author(f'Admin of {info_data[CONDO_NAME_STRING]}')

    residents = []
    for user in users_repository.get_users(tenant):
        if user.get_unit() == 0:
            continue
        else:
            residents.append(user)

    # sort residents list by unit number
    residents.sort(key=sort_residents)

    # print the report
    img_name = f"{tenant}/{UNPROTECTED_FOLDER}/branding/logo.jpg"
    pdf.print_report(aws.read_binary_obj(img_name), info_data, residents)

#    pdf.output(CENSUS_FORMS_PDF_FULL_PATH, 'F')
    pdf_obj = pdf.output(dest='S').encode('latin-1')
    pdf_path = f"{tenant}/{CENSUS_FORMS_PDF_FULL_PATH}"
    aws.upload_binary_obj(pdf_path, pdf_obj)

    print(f"generated pdf file in {pdf_path}")

    # update the info.json file
    date = datetime.today().strftime('%d-%b-%Y')
    info_data[CENSUS_FORMS_DATE_STRING] = date
    info_obj = get_json_from_file_no_tenant(f"{INFO_FILE}")
    info_obj['config'][tenant] = info_data
    save_json_to_file_no_tenant(INFO_FILE, info_obj)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

@app.route('/<tenant>/checkpdf', methods=['GET'])
def download_pdf(tenant):
    lock.acquire()

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    if not aws.is_file_found(f"{tenant}/{CENSUS_FORMS_PDF_FULL_PATH}"):
        return_obj = json.dumps({'response': {'status': 'file_not_found'}})
    else:
        return_obj = json.dumps({'response': {'status': 'success', 'pdf_full_path': f"{tenant}/{CENSUS_FORMS_PDF_FULL_PATH}"}})
    #return send_from_directory('static', rel_path)
    lock.release()
    return return_obj


@app.route('/<tenant>/login', methods=['GET' , 'POST'])
def login_tenant(tenant):
    # print(f"here in login_tenant(), {request.path}")
    lock.acquire()

    # check to see if the tenant even exists in our database
    if not is_tenant_found(tenant):
        page_content = render_template("condo_not_found.html", tenant=tenant)
        lock.release()
        return page_content

    if request.method == 'GET':
        if current_user.is_authenticated:
            # print(f"login_tenant(): there is a user already logged in: {current_user.id}")
            next_page = request.args.get('next') if request.args.get('next') is not None else f'/{tenant}/home'
            lock.release()
            return redirect(next_page)
        else:
            info_data = get_info_data(tenant)
            lock.release()
            return render_template('login.html', info_data=info_data)

    # if request.method == 'GET':
    #     tenant = get_tenant_from_url()
    #     next_tenant = get_tenant_from_next()
    #
    #     if tenant is None and next_tenant is None:
    #         lock.release()
    #         return render_template('login_tenant.html')
    #     else:
    #         lock.release()
    #         return render_template('login.html')


    # from here on down, it's a POST request
    if current_user.is_authenticated:
        # print(f"login_tenant(): there is a user already logged in: {current_user.id}")
        next_page = request.args.get('next') if request.args.get('next') is not None else f'/{tenant}/home'
        lock.release()
        return redirect(next_page)

    # print(f"login_tenant(): current_user {current_user} is not authenticated")
    userid = request.form['userid']
    password = request.form['password']
    load_users(tenant)

    # if 'tenant' in session and session['tenant'] == tenant:
    # if is_user_logged_in(tenant, users_repository.get_user_by_userid(tenant, userid)):
    #     print(f"login_tenant(): tenant {tenant} is already logged in")
    #     lock.release()
    #     return redirect(f"/{tenant}/home")

    # print(f"login_tenant(): tenant: {tenant}, userid: {userid}")
    info_data = get_info_data(tenant)
    registered_user = users_repository.get_user_by_userid(tenant, userid)

    if registered_user is None:
        flash("Invalid userid or password")
        lock.release()
        return render_template("login.html", info_data=info_data)

    if registered_user.password == password:
        next_page = request.args.get('next') if request.args.get('next') is not None else f'/{tenant}/home'
        msg = f'user {registered_user.userid} logged in'
        log(tenant, msg)
        registered_user.authenticated = True
        login_user(registered_user)
        # add_to_logged_in_users(tenant, registered_user)
        session["tenant"] = tenant
        session['userid'] = userid
        # print(f"login_tenant(): we just logged in {session['userid']} of tenant {session['tenant']}, session obj: {session}")
        lock.release()
        return redirect(next_page)
    else:
        #return abort(401)
        flash("Invalid userid or password")
        lock.release()
        return render_template("login.html", info_data=info_data)


@app.route('/<tenant>/forgot_password', methods=['GET', 'POST'])
def forgot_password(tenant):
    lock.acquire()
    print(f"here in forgot_password(): {tenant}")

    if not is_tenant_found(tenant):
        lock.release()
        return render_template("condo_not_found.html", tenant=tenant)

    info_data = get_info_data(tenant)
    if request.method == 'GET':
        info_data['loggedin-userdata'] = { 'tenant': tenant}
        lock.release()
        return render_template("forgot_password.html", info_data=info_data, msg="An email will be sent to the email on file for the user id entered above")

    json_obj = request.get_json()
    user_id = json_obj['request']['user_id']
    req_tenant = json_obj['request']['tenant']

    print(f"tenant {req_tenant},  user_id {user_id}")

    load_users(tenant)
    user = users_repository.get_user_by_userid(tenant, user_id)

    if user is None:
        return_obj = json.dumps({'response': {'status': 'error', 'message': "Record not found for User Id"}})
        lock.release()
        return return_obj

    if len(user.email.strip()) == 0:
        return_obj = json.dumps({'response': {'status': 'error', 'message': "No email registered for user. Contact the Admin."}})
        lock.release()
        return return_obj

    if info_data['language'] == 'pt':
        body = f"Mensagem do CondoSpace.app. \nAbaixo estão as credenciais de login. Se você não solicitou, ignore este email ou avise o Administrador do website.\n\n"
        body += f"Usuário: {user.userid}\n"
        body += f"Senha: {user.password}\n"
        subject = 'Mensagem do CondoSpace.app'
    elif info_data['language'] == 'en':
        body = f"Message from the CondoSpace App. Below are your credentials. If you didn't request it, ignore this email or inform the website admin.\n\n"
        body += f"Your User Id: {user.userid}\n"
        body += f"Your Password: {user.password}\n"
        subject = 'Message from CondoSpace.app'
    else:
        return_obj = json.dumps({'response': {'status': 'error', 'message': f"Preferred language not found in the system. Contact the website administrator."}})
        lock.release()
        return return_obj

    send_email_redmail(user.email, subject, body)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj



'''
  These are simply supporting functions (i.e not related to GET or POST).
  TO DO: This needs to be enhanced so it logs messages to the specific tenant folder in the cloud.
'''
def log(tenant, msg):
    timestamp = get_timestamp()
    if aws.is_file_found(f"{tenant}/{LOG_FILE}"):
        log_text = aws.read_text_obj(f"{tenant}/{LOG_FILE}")
    else:
        log_text = ""    
    log_text += f'{timestamp} {msg}\n'
    aws.upload_text_obj(f"{tenant}/{LOG_FILE}", log_text)

def get_timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def get_epoch_from_now():
    return calendar.timegm(datetime.now().timetuple())

def get_epoch_from_string(date_string):
    date_format = "%Y-%m-%d"
    datetime_object = datetime.strptime(date_string, date_format)
    epoch_timestamp = int(time.mktime(datetime_object.timetuple()))
    return epoch_timestamp

# rather than simply converting to DD-MM-YYYY
def get_string_from_epoch(epoch_timestamp, lang='en'):
    if lang == 'pt':
        date_format = '%d-%m-%Y'
    elif lang == 'en':
        date_format = '%m-%d-%Y'
    else:
        date_format = '%m-%d-%Y'
    return datetime.fromtimestamp(int(epoch_timestamp)).strftime(date_format)

def get_string_from_epoch_format(epoch_timestamp, date_format):
    return datetime.fromtimestamp(int(epoch_timestamp)).strftime(date_format)

def get_date_dict_from_epoch(epoch_timestamp):
    str_date = get_string_from_epoch_format(epoch_timestamp, '%Y%m%d')
    date_dict = { 'y': int(str_date[:4]), 'm': int(str_date[4:6]), 'd': int(str_date[6:8]) }
    return date_dict

def send_email_relay_host(emailto, subject, body):
    TO = emailto
    SUBJECT = subject
    BODY = body
    HOST = "localhost"

    # prepare message
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = WHITEGATE_NAME + ' <' + WHITEGATE_EMAIL + '>'
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY))
    email_list = TO.split(',') # creates a list from a comma-separated string

    # connect to server
    server = smtplib.SMTP(HOST)

    # now send email
    response = server.sendmail(WHITEGATE_EMAIL, email_list, msg.as_string())
    server.quit()

def send_email_redmail(email_to, subject, body):
    gmail.username = BLUERIVER_CONTACT_EMAIL
    gmail.password = BLUERIVER_CONTACT_PASSWORD
    gmail.send(receivers=[email_to, 'info@condospace.app'], subject=subject, text=body)

def send_email_redmail_all(email_list, subject, body):
    gmail.username = BLUERIVER_CONTACT_EMAIL
    gmail.password = BLUERIVER_CONTACT_PASSWORD
    gmail.send(bcc=email_list, subject=subject, text=body)


# THIS DIDN'T WORK
def send_email_google(email_to, subject, body):
    email_host = 'smtp_gmail.com'
    tls_port = 587
    ssl_port = 465
    FROM = GMAIL_BLUERIVER_EMAIL
    TO = email_to
    SUBJECT = subject
    BODY = body

    # prepare message
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY))
    email_list = TO.split(',') # creates a list from a comma-separated string

    # google gmail credentials
    email_user = GMAIL_BLUERIVER_EMAIL
    password = "anda ppxi wyab wyla"

    # these are used with SSL
    server = smtplib.SMTP('smtp_gmail.com:587')
    server.starttls()
    server.login(GMAIL_BLUERIVER_EMAIL, 'anda ppxi wyab wyla')
    server.ehlo()
    #server.login(user, password)

    # now send email
    response = server.sendmail(FROM, email_list, msg.as_string())
    print(f"email server response: {response}")
    server.quit()


def send_email_local(email_to, subject, body, email_server, port, user, password):
    FROM = GMAIL_BLUERIVER_EMAIL
    TO = email_to
    SUBJECT = subject
    BODY = body

    # prepare message
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY))
    email_list = TO.split(',') # creates a list from a comma-separated string

    server = smtplib.SMTP(email_server, port)
    server.ehlo()

    # now send email
    response = server.sendmail(FROM, email_list, msg.as_string())
    print(f"email server response: {response}")
    server.quit()


def get_all_emails():
    all_emails = []
    for user in users_repository.get_users():
#        user = users_repository.get_user_by_unit(key)
        email = user.email.strip()
        if len(email):
            all_emails.append(email)
    msg = f'all emails {all_emails}'

    # TODO: fix this
    log('demo', msg)
    return all_emails


def sort_criteria(obj):
    return obj['userid']


def generate_password(userid):
    number = randint(1, 9999)
    if number < 10:
        numberStr = "000" + str(number)
    elif number < 100:
        numberStr = "00" + str(number)
    elif number < 1000:
        numberStr = "0" + str(number)
    else:
        numberStr = str(number)
    return f"{userid}@{numberStr}"


# handle login failed
@app.errorhandler(401)
def login_failed(e):
    return Response('<p>Login failed</p>')


# handle page not found
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 4

@app.before_request
def before_request():
    # tenant_s = session['tenant'] if 'tenant' in session else None
    # if tenant_s is None:
    #     tenant_s = get_tenant_from_url()
    # print(f"before_request(): tenant: {tenant_s}, path: {request.path}")
    session.permanent = True # doesn't destroy the session when the browser window is closed
    app.permanent_session_lifetime = timedelta(hours=2)
    session.modified = True  # resets the session timeout timer
    # global logged_in_users
    # logged_in_users[current_user] = current_user

# callback to reload the user object
# internal_user_id is the sequential number given to a user when it is added to the system
@login_manager.user_loader
def load_user(internal_user_id):
    # tenant_s = session['tenant'] if 'tenant' in session else None
    # userid_s = session['userid'] if 'userid' in session else None
    # tenant = composite_id[:composite_id.find('-')]
    # print(f"load_user(): url: {request.path}, composite_id {composite_id}, tenant {tenant}, tenant_s {tenant_s}, user_s {userid_s}")

    print(f"internal_user_id: {internal_user_id}")
    tenant = get_tenant()
    print(f"tenant: {tenant}")

    if tenant == 'root':
        return None

    load_users(tenant)
    user = users_repository.get_user_by_id(tenant, internal_user_id)
    if user is None:
        print("in load_user(): failure in getting the user")
        log(tenant, "in load_user(): something is wrong with our user\n")
        ret_user = None
    else:
        ret_user = user
    return ret_user

def get_files(tenant, folder, pattern):
    files = aws.get_file_list_folder(tenant, folder)
    if pattern:
        arr = [x for x in files if x.startswith(f"{BUCKET_PREFIX}/{get_tenant()}/{folder}/{pattern}")]
    else:
        arr = files
    files_arr = []
    for file in arr:
        files_arr.append(os.path.basename(file))    
    files_arr.sort()
    return files_arr
    

# This is invoked by Babel
def get_locale():
    if request.path == '/register_pt' or request.path == '/about_pt':
        return "pt"
    if request.path == '/register_en' or request.path == '/about_en':
        return "en"
    #print(f"get_locale(): tenant {tenant_global}")
    if not is_tenant_found(tenant_global):
        return "en"
    info_data = get_info_data(tenant_global)
    return info_data['language']

"""Translate text.
Returns:
    str: translated text
"""
def translate():
    #print("here in translate")
    text = request.form['text']
    translated = lazy_gettext(text)
    return str(translated)


# this call cannot be inside main() because this will run with gunicorn in PROD
babel = Babel(app, locale_selector=get_locale)
_ = lazy_gettext

def test_new_users_rep():
    users_repo = UsersRepository(aws)
    users_repo.load_users('belavista')
    users_repo.load_users('demo')
    for user in users_repo.get_users('belavista'):
        print(f"user: id {user.id}, userid {user.userid}, unit {user.unit}, {user.name}, {user.email}")
    user = users_repo.get_user_by_id('belavista', 'belavista-unitA1')
    print(f"user id 2:         id {user.id}, userid {user.userid}, unit {user.unit}, name {user.name}, email {user.email}")
    user = users_repo.get_user_by_unit('belavista', 0)
    print(f"user unit 0:       id {user.id}, userid {user.userid}, unit {user.unit}, name {user.name}, email {user.email}")
    user = users_repo.get_user_by_userid('belavista', 'unitA3')
    print(f"user unit unitA3:  id {user.id}, userid {user.userid}, unit {user.unit}, name {user.name}, email {user.email}")
    user = users_repo.get_user_by_id(f"{'belavista'}@{'unitA4'}")
    print(f"user composite:  id {user.id}, userid {user.userid}, unit {user.unit}, name {user.name}, email {user.email}")

    print(f"\ndata for demo:")
    for user in users_repo.get_users('demo'):
        print(f"id: {user.id}, userid {user.userid}, unit {user.unit}, {user.name}, {user.email}")

    print(f"\ndata for belavista:")
    user = users_repo.get_user_by_id(f"{'belavista'}@{'unitA1'}")

    print(f"\n user count in belavista: {users_repo.get_user_count_by_tenant('belavista')}")
    print(f"\n total user count: {users_repo.get_user_count_total()}")


def create_app():
    app_name = 'server.py'
    print(f"app name: {app_name}")
    return app


'''
  host='0.0.0.0' means "accept connections from any client ip address".
'''
# def main():
#     # we need to tell Babel which function to call for "locale_selector"
#     app.run(host='0.0.0.0', debug=False)
#
# if __name__ == '__main__':
#     main()

