
import requests
from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from threading import Lock
from aws import AWS
import json

from users import UsersRepository
from users_adm import UsersRepository as UsersAdmRepository
from datetime import timedelta, datetime
from server import get_string_from_epoch
from server import get_epoch_from_string
from server import get_string_from_epoch_format

CONFIG_FOLDER = 'config'
SERVER_FOLDER = 'serverfiles'
UPLOADED_FOLDER = 'uploadedfiles'
PROTECTED_FOLDER = f"{UPLOADED_FOLDER}/protected"
INFO_FILE = "info.json"

# all files in the "config" folder
# When running locally, the "config" folder must be in the File System.
# When running on the cloud, the "config" folder is in the docker file
CONFIG_FILE =   f"{CONFIG_FOLDER}/config.json"

BUCKET_PREFIX = "customers"

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

app = Flask(
            __name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates'
           )

app.config['SECRET_KEY'] = config['flask_secret_key']
app.url_map.strict_slashes = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = (u'Due to inactivity, you have been logged out. Please login again')
login_manager.login_message = 'Login is required to access the page you want'
login_manager.needs_refresh_message_category = 'info'

aws = AWS(BUCKET_PREFIX, config['bucket_name'], config['aws_access_key_id'], config['aws_secret_access_key'])

# define user repository
users_repository = UsersRepository(aws)

# define user repository (for special tenant 'adm')
users_adm_repository = UsersAdmRepository(aws)

# define the lock object
lock = Lock()

'''
 For now, the users of this application will be in the file 'residents.json'
 which is located in the special folder 'adm'
'''
def load_users(tenant):
    if users_adm_repository.is_tenant_loaded(tenant):
        return
    users_adm_repository.load_users(tenant)
    print(f"just loaded tenant {tenant} into users_adm_repository")

def get_json_from_file(file_path):
    if not aws.is_file_found(file_path):
        return None
    string_content = aws.read_text_obj(file_path)
    return json.loads(string_content)

def save_json_to_file(file_path, content):
    string_content = json.dumps(content)
    resp = aws.upload_text_obj(file_path, string_content)
    return resp

def get_info_data(tenant):
    if not aws.is_file_found(f"{INFO_FILE}"):
        print(f"get_info_data(): file not found: {INFO_FILE},  tenant: {tenant}")
        return None
    json_obj = get_json_from_file(f"{INFO_FILE}")
    return json_obj


#-----------------------------------------------------------------------------------------------------
#     File related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/common/img/<filename>')
def static_image_files(filename):
    file_obj = open(f"{app.static_folder}/img/{filename}", "rb")
    return Response(response=file_obj, status=200, mimetype="image/jpg")


#-----------------------------------------------------------------------------------------------------
#     Login/Logout related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/')
def home():
    lock.acquire()
    page = redirect("login")
    lock.release()
    return page

@app.route('/login', methods=['GET' , 'POST'])
def login():
    lock.acquire()
    if request.method == 'GET':
        if current_user.is_authenticated:
            # print(f"login_tenant(): there is a user already logged in: {current_user.id}")
            next_page = request.args.get('next') if request.args.get('next') is not None else '/customers'
            lock.release()
            return redirect(next_page)
        else:
            info_data = get_info_data('adm')
            lock.release()
            return render_template('adm/login.html', info_data=info_data)

    # from here on down, it's a POST request
    if current_user.is_authenticated:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/customers'
        lock.release()
        return redirect(next_page)

    userid = request.form['userid']
    password = request.form['password']
    load_users('adm')
    registered_user = users_adm_repository.get_user_by_userid('adm', userid)

    if registered_user.password == password:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/customers'
        registered_user.authenticated = True
        login_user(registered_user)
        lock.release()
        print("password matches!")
        return redirect(next_page)
    else:
        #return abort(401)
        flash("Invalid userid or password")
        lock.release()
        return render_template("adm/login.html", info_data=get_info_data('adm'))


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect("login")

    # from here on down we know that an user is logged in
    print(f"user to be logged out: {current_user.userid}")

    current_user.authenticated = False
    userid = current_user.userid  # we need to save the userid BEFORE invoking logout_user()
    logout_user()
    return render_template("adm/logout.html", loggedout_user=userid, info_data=get_info_data('adm'))


#-----------------------------------------------------------------------------------------------------
#     Customer related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/customers')
@login_required
def get_customers():
    lock.acquire()
    print(f"here in get_customers()")
    customers = get_json_from_file(f"{INFO_FILE}")
    customers_arr = []

    for key, customer in customers['config'].items():
        if key == 'adm':
            continue
        if 'adm_userid' in customer:
            tenant = customer['domain']
            user_id = customer['adm_userid']
            users_repository.load_users(tenant)
            user = users_repository.get_user_by_userid(tenant, user_id)
            customer['adm_pass'] = user.password
            customer['adm_email'] = user.email
            customer['adm_phone'] = user.phone
        else:
            customer['adm_userid'] = ''
            customer['adm_pass'] = ''
            customer['adm_email'] = ''
            customer['adm_phone'] = ''

        #print(f"license_pay_date: {customer['license_pay_date']}")
        customer['registration_date'] = get_string_from_epoch(customer['registration_date'])
        customer['license_pay_date'] = get_string_from_epoch(customer['license_pay_date']) if customer['license_pay_date'] else None
        customers_arr.append(customer)

    info_data = get_info_data("adm")
    info_data['is_authenticated'] = True
    lock.release()
    return render_template("adm/customers.html", customers=customers_arr, info_data=info_data)

@app.route('/save_customer', methods=["POST"])
@login_required
def save_customer():
    lock.acquire()
    prefix = 'customer'
    json_obj = request.get_json()
    tenant = json_obj[prefix]['tenant']
    user_id = json_obj[prefix]['user_id']
    user_pass = json_obj[prefix]['user_pass']
    user_email = json_obj[prefix]['user_email']
    user_phone = json_obj[prefix]['user_phone']
    lic_date_year = json_obj[prefix]['date']['y']
    lic_date_month = json_obj[prefix]['date']['m']
    lic_date_day = json_obj[prefix]['date']['d']
    lic_amount = json_obj[prefix]['lic_amount']
    lic_term = json_obj[prefix]['lic_term']

    #print(f"tenant: {tenant}, {lic_date_year} / {lic_date_month} / {lic_date_day} {user_id}")

    # read the INFO_FILE to update the info
    if not aws.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    info_data = get_json_from_file(f"{INFO_FILE}")
    if lic_date_year and lic_date_month and lic_date_day:
        date_string = f"{lic_date_year}-{lic_date_month}-{lic_date_day}"
        info_data['config'][tenant]['license_pay_date'] = get_epoch_from_string(date_string)
    if lic_amount:
        info_data['config'][tenant]['license_pay_amount'] = lic_amount
    if lic_term:
        info_data['config'][tenant]['license_term'] = lic_term
    save_json_to_file(INFO_FILE, info_data)
    return_obj = json.dumps({'response': {'status': 'success'}})

    #print(f"license_pay_date: {info_data['config'][tenant]['license_pay_date']}")
    lock.release()
    return return_obj


@app.route('/retrieve_customer', methods=["POST"])
@login_required
def retrieve_customer():
    lock.acquire()
    print(f"here in retrieve_customer()")
    prefix = 'customer'
    json_obj = request.get_json()
    tenant = json_obj[prefix]['tenant']

    # read the INFO_FILE to update the info
    if not aws.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    customer = get_json_from_file(f"{INFO_FILE}")['config'][tenant]

    if 'adm_userid' in customer:
        users_repository.load_users(customer['domain'])
        user = users_repository.get_user_by_userid(customer['domain'], customer['adm_userid'])
        customer['adm_pass'] = user.password
        customer['adm_email'] = user.email
        customer['adm_phone'] = user.phone
    else:
        customer['adm_userid'] = ''
        customer['adm_pass'] = ''
        customer['adm_email'] = ''
        customer['adm_phone'] = ''

    lic_pay_date = get_string_from_epoch_format(customer['license_pay_date'], '%Y-%m-%d') if customer['license_pay_date'] else ''
    response = {
        'status': 'success',
        'adm_userid': customer['adm_userid'],
        'adm_pass': customer['adm_pass'],
        'adm_email': customer['adm_email'],
        'adm_phone': customer['adm_phone'],
        'license_pay_date': lic_pay_date,
        'license_pay_amount': customer['license_pay_amount'],
        'license_term': customer['license_term']
    }

    return_obj = json.dumps( {'response': response} )
    lock.release()
    return return_obj


#-----------------------------------------------------------------------------------------------------
#     Login related routines
#-----------------------------------------------------------------------------------------------------
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
    session.permanent = True # doesn't destroy the session when the browser window is closed
    app.permanent_session_lifetime = timedelta(hours=2)
    session.modified = True  # resets the session timeout timer


# callback to reload the user object
# internal_id is the sequential number given to a user when it is added to the system
@login_manager.user_loader
def load_user(internal_id):
    load_users('adm')
    user = users_adm_repository.get_user_by_id("adm", internal_id)
    if user is None:
        print("in load_user(): failure in getting the user")
        ret_user = None
    else:
        ret_user = user

    print(f"user id {internal_id} found!")
    return ret_user


def create_app():
    app_name = 'server_adm_1'
    print(f"app name: {app_name}")

    # create app
    app = Flask(__name__, instance_relative_config=True)

    return app

'''
  host='0.0.0.0' means "accept connections from any client ip address".
'''
def main():
    app.run(host='0.0.0.0', port=8080, debug=False)

if __name__ == '__main__':
    main()
