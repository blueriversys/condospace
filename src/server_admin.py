
import requests
from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

from threading import Lock
from aws import AWS
import json

from users import UsersRepository
from users_adm import UsersRepository as UsersAdmRepository
from datetime import timedelta, datetime
from server import is_tenant_found, config, users_repository_mtadmin, aws_mtadmin, get_string_from_epoch, get_string_from_epoch_format, get_epoch_from_string

CONFIG_FOLDER = 'config'
SERVER_FOLDER = 'serverfiles'
INFO_FILE = "info.json"

BUCKET_PREFIX = "customers"
CUSTOMERS_PER_PAGE = 20

# all files in the "config" folder
# When running locally, the "config" folder must be in the File System.
# When running on the cloud, the "config" folder is in the docker file
#CONFIG_FILE =   f"{CONFIG_FOLDER}/config.json"

# for PROD, change the file serverfiles/config-prod.dat
# with open(CONFIG_FILE, 'r') as f:
#     config_file_content = f.read()
#     config = json.loads(config_file_content)['config']
#     print(f"\nSome of the config vars:")
#     print(f"API Url: {config['api_url']}")
#     print(f"API app type: {config['api_app_type']}")
#     print(f"AWS bucket name: {config['bucket_name']}")
#     print(f"Domain name: {config['domain']}")
#     print(f"Version #: {config['version']['number']},  version date: {config['version']['date']}")

app = Flask(
            __name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates/admin'
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

def get_json_from_file_mtadmin(file_path):
    if not aws_mtadmin.is_file_found(file_path):
        return None
    string_content = aws_mtadmin.read_text_obj(file_path)
    return json.loads(string_content)

def save_json_to_file(file_path, content):
    string_content = json.dumps(content, indent=4, ensure_ascii=False)
    resp = aws.upload_text_obj(file_path, string_content)
    return resp

def save_json_to_file_mtadmin(file_path, content):
    string_content = json.dumps(content, indent=4, ensure_ascii=False)
    resp = aws_mtadmin.upload_text_obj(file_path, string_content)
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
def home_root():
    print("here in server_admin.home_root()")
    return redirect("/admin/customers")

@app.route('/root')
def home():
    print("here in server_admin.home()")
    return redirect("/admin/customers")

@app.route('/customers/login', methods=['GET' , 'POST'])
def login():
    lock.acquire()
    print("here in server_admin.login()")
    if request.method == 'GET':
        if current_user.is_authenticated:
            # print(f"login_tenant(): there is a user already logged in: {current_user.id}")
            next_page = request.args.get('next') if request.args.get('next') is not None else '/admin/customers/condo'
            lock.release()
            return redirect(next_page)
        else:
            info_data = get_info_data('adm')
            lock.release()
            return render_template('login.html', info_data=info_data)

    # from here on down, it's a POST request
    if current_user.is_authenticated:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/admin/customers/condo'
        lock.release()
        return redirect(next_page)

    userid = request.form['userid']
    password = request.form['password']
    load_users('adm')
    registered_user = users_adm_repository.get_user_by_userid('adm', userid)

    if registered_user is None:
        flash("Invalid user or password")
        lock.release()
        return render_template("login.html", info_data=get_info_data('adm'))

    if registered_user.password == password:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/admin/customers/condo'
        registered_user.authenticated = True
        login_user(registered_user)
        lock.release()
        print("password matches!")
        return redirect(next_page)
    else:
        #return abort(401)
        flash("Invalid userid or password")
        lock.release()
        return render_template("login.html", info_data=get_info_data('adm'))


@app.route('/customers/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect("login")

    # from here on down we know that an user is logged in
    print(f"user to be logged out: {current_user.userid}")

    current_user.authenticated = False
    userid = current_user.userid  # we need to save the userid BEFORE invoking logout_user()
    logout_user()
    return render_template("logout.html", loggedout_user=userid, info_data=get_info_data('adm'))


#-----------------------------------------------------------------------------------------------------
#     Customer related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/customers/condo')
@login_required
def get_condo_customers():
    lock.acquire()
    print(f"here in server_admin.get_condo_customers()")
    customers_arr = []
    info_data = get_info_data("adm")
    customers = get_json_from_file(f"{INFO_FILE}")
    added_count = 0

    for key, customer in customers['config'].items():
        if key == 'adm':
            continue

        if 'admin_userid' in customer:
            tenant = key
            if not aws.is_file_found(tenant):
                continue
            user_id = customer['admin_userid']
            if not is_tenant_found(tenant):
                print(f"Tenant {tenant} not found, skipping load_users()")
                continue
            print(f"will now load_users() for tenant {tenant}")
            users_repository.load_users(tenant)
            #print(f"step 2. tenant: {tenant}   user_id: {user_id}")
            # todo: MELHORAR ESTA FUNCAO, TRAVANDO QUANDO O USER_ID NAO EXISTE
            user = users_repository.get_user_by_userid(tenant, user_id)
            customer['admin_pass'] = user.password
            customer['admin_email'] = user.email
            customer['admin_phone'] = user.phone
        else:
            customer['admin_userid'] = ''
            customer['admin_pass'] = ''
            customer['admin_email'] = ''
            customer['admin_phone'] = ''

        #print(f"license_pay_date: {customer['license_pay_date']}")
        customer['registration_date'] = get_string_from_epoch(customer['registration_date'])
        customer['last_login_date'] = get_string_from_epoch(customer['last_login_date'])
        customer['license_pay_date'] = get_string_from_epoch(customer['license_pay_date']) if customer['license_pay_date'] else None
        customers_arr.append(customer)
        added_count += 1
        if added_count == CUSTOMERS_PER_PAGE:
            break

    info_data['is_authenticated'] = True
    lock.release()
    return render_template("customers_condo.html", page=1, customers=customers_arr, info_data=info_data)


@app.route('/customers/company')
@login_required
def get_company_customers():
    lock.acquire()
    print(f"here in server_admin.get_company_customers()")
    customers_arr = []
    info_data = get_info_data("adm")
    customers = get_json_from_file_mtadmin(f"{INFO_FILE}")
    added_count = 0

    for key, customer in customers['companies'].items():
        users_list = customers['users_by_company'][key]['users']
        user_id = users_list[0]
        customer['domain'] = key
        customer['admin_userid'] = user_id
        customer['admin_pass'] = customers['users'][user_id]['password']
        customer['admin_email'] = customers['users'][user_id]['email']
        customer['registration_date'] = get_string_from_epoch(customer['registration_date'])
        customer['last_login_date'] = get_string_from_epoch(customers['users'][user_id]['last_login_date']) if customers['users'][user_id]['last_login_date'] else None
        customer['license_pay_date'] = get_string_from_epoch(customer['license_pay_date']) if customer['license_pay_date'] else None
        customers_arr.append(customer)
        added_count += 1
        if added_count == CUSTOMERS_PER_PAGE:
            break

    info_data['is_authenticated'] = True
    lock.release()
    return render_template("customers_company.html", page=1, customers=customers_arr, info_data=info_data)


@app.route('/customers/condo/<string:reg_date>/<int:page>', methods=["POST"])
@login_required
def get_customers_page(reg_date, page):
    lock.acquire()
    print(f"here in server_admin.get_customers(), reg_date {reg_date}  page {page}")
    customers_arr = []
    info_data = get_info_data("adm")
    customers = get_json_from_file(f"{INFO_FILE}")
    # a page comprises 30 customers
    # page 1 = from 0  to 30
    # page 2 = from 31 to 60 (skip 30)
    # page 3 = from 61 to 90 (skip 60)
    # skip_count = page * 30 - 30

    skip_count = page * CUSTOMERS_PER_PAGE - CUSTOMERS_PER_PAGE
    print(f"skip_count: {skip_count}")
    count = 0
    added_count = 0

    for key, customer in customers['config'].items():
        if key == 'adm':
            continue

        if reg_date != "00000000":
            cust_reg_date = get_string_from_epoch_format(customer['registration_date'], '%Y%m%d')
            if cust_reg_date != reg_date:
                continue

        if count < skip_count:
            count += 1
            continue

        if 'admin_userid' in customer:
            tenant = key
            if not aws.is_file_found(tenant):
                continue
            user_id = customer['admin_userid']
            if not is_tenant_found(tenant):
                print(f"Tenant {tenant} not found, skipping load_users()")
                continue
            users_repository.load_users(tenant)
            # todo: MELHORAR ESTA FUNCAO, TRAVANDO QUANDO O USER_ID NAO EXISTE
            user = users_repository.get_user_by_userid(tenant, user_id)
            customer['admin_pass'] = user.password
            customer['admin_email'] = user.email
            customer['admin_phone'] = user.phone
        else:
            customer['admin_userid'] = ''
            customer['admin_pass'] = ''
            customer['admin_email'] = ''
            customer['admin_phone'] = ''

        # for DEBUG purposes
        print(f"epoch timestamp: {customer['registration_date']}")
        print(f"from epoch_format: {get_string_from_epoch_format(customer['registration_date'], '%Y%m%d')}")
        print(f"from epoch       : {get_string_from_epoch(customer['registration_date'])}")

        #print(f"license_pay_date: {customer['license_pay_date']}")
        customer['registration_date'] = get_string_from_epoch(customer['registration_date'])
        customer['last_login_date'] = get_string_from_epoch(customer['last_login_date'])
        customer['license_pay_date'] = get_string_from_epoch(customer['license_pay_date']) if customer['license_pay_date'] else None
        customers_arr.append(customer)
        added_count += 1
        if added_count == CUSTOMERS_PER_PAGE:
            break

    print(f"size of array to return: {len(customers_arr)}")
    info_data['is_authenticated'] = True
    return_obj = json.dumps({'response': {'status': 'success', 'customers': customers_arr}})
    lock.release()
    return return_obj

@app.route('/customers/company/<string:reg_date>/<int:page>', methods=["POST"])
@login_required
def get_customers_company_page(reg_date, page):
    lock.acquire()
    print(f"here in server_admin.get_customers(), reg_date {reg_date}  page {page}")
    customers_arr = []
    info_data = get_info_data("adm")
    customers = get_json_from_file(f"{INFO_FILE}")
    # a page comprises 30 customers
    # page 1 = from 0  to 30
    # page 2 = from 31 to 60 (skip 30)
    # page 3 = from 61 to 90 (skip 60)
    # skip_count = page * 30 - 30

    skip_count = page * CUSTOMERS_PER_PAGE - CUSTOMERS_PER_PAGE
    print(f"skip_count: {skip_count}")
    count = 0
    added_count = 0

    for key, customer in customers['config'].items():
        if key == 'adm':
            continue

        if reg_date != "00000000":
            cust_reg_date = get_string_from_epoch_format(customer['registration_date'], '%Y%m%d')
            if cust_reg_date != reg_date:
                continue

        if count < skip_count:
            count += 1
            continue

        if 'admin_userid' in customer:
            tenant = key
            if not aws.is_file_found(tenant):
                continue
            user_id = customer['admin_userid']
            if not is_tenant_found(tenant):
                print(f"Tenant {tenant} not found, skipping load_users()")
                continue
            users_repository.load_users(tenant)
            # todo: MELHORAR ESTA FUNCAO, TRAVANDO QUANDO O USER_ID NAO EXISTE
            user = users_repository.get_user_by_userid(tenant, user_id)
            customer['admin_pass'] = user.password
            customer['admin_email'] = user.email
            customer['admin_phone'] = user.phone
        else:
            customer['admin_userid'] = ''
            customer['admin_pass'] = ''
            customer['admin_email'] = ''
            customer['admin_phone'] = ''

        # for DEBUG purposes
        print(f"epoch timestamp: {customer['registration_date']}")
        print(f"from epoch_format: {get_string_from_epoch_format(customer['registration_date'], '%Y%m%d')}")
        print(f"from epoch       : {get_string_from_epoch(customer['registration_date'])}")

        #print(f"license_pay_date: {customer['license_pay_date']}")
        customer['registration_date'] = get_string_from_epoch(customer['registration_date'])
        customer['last_login_date'] = get_string_from_epoch(customer['last_login_date'])
        customer['license_pay_date'] = get_string_from_epoch(customer['license_pay_date']) if customer['license_pay_date'] else None
        customers_arr.append(customer)
        added_count += 1
        if added_count == CUSTOMERS_PER_PAGE:
            break

    print(f"size of array to return: {len(customers_arr)}")
    info_data['is_authenticated'] = True
    return_obj = json.dumps({'response': {'status': 'success', 'customers': customers_arr}})
    lock.release()
    return return_obj

@app.route('/customers/condo/save_customer', methods=["POST"])
@login_required
def save_customer_condo():
    lock.acquire()
    print(f"here in server_admin.save_customer_condo()")
    prefix = 'customer'
    json_obj = request.get_json()
    tenant = json_obj[prefix]['tenant']
    user_id = json_obj[prefix]['user_id']
    user_pass = json_obj[prefix]['user_pass']
    user_email = json_obj[prefix]['user_email']
    user_phone = json_obj[prefix]['user_phone']
    lic_date = json_obj[prefix]['date']  # in the format YYYY-MM-DD
    lic_amount = json_obj[prefix]['lic_amount']
    lic_term = json_obj[prefix]['lic_term']

    #print(f"tenant: {tenant}, {lic_date_year} / {lic_date_month} / {lic_date_day} {user_id}")

    # read the INFO_FILE to update the info
    if not aws.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    info_data = get_json_from_file(f"{INFO_FILE}")
    if lic_date:
        print(f"string date: {lic_date}")
        info_data['config'][tenant]['license_pay_date'] = get_epoch_from_string(lic_date)
    if lic_amount:
        info_data['config'][tenant]['license_pay_amount'] = lic_amount
    if lic_term:
        info_data['config'][tenant]['license_term'] = lic_term
    save_json_to_file(INFO_FILE, info_data)
    return_obj = json.dumps({'response': {'status': 'success'}})

    #print(f"license_pay_date: {info_data['config'][tenant]['license_pay_date']}")
    lock.release()
    return return_obj


@app.route('/customers/company/save_customer', methods=["POST"])
@login_required
def save_customer_company():
    lock.acquire()
    print(f"here in server_admin.save_customer_company()")
    prefix = 'customer'
    json_obj = request.get_json()
    company_id = json_obj[prefix]['tenant']
    user_id = json_obj[prefix]['user_id']
    user_pass = json_obj[prefix]['user_pass']
    user_email = json_obj[prefix]['user_email']
    user_phone = json_obj[prefix]['user_phone']
    lic_date = json_obj[prefix]['date']  # in the format YYYY-MM-DD
    lic_amount = json_obj[prefix]['lic_amount']
    lic_term = json_obj[prefix]['lic_term']

    # read the INFO_FILE to update the info
    if not aws_mtadmin.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    info_data = get_json_from_file_mtadmin(f"{INFO_FILE}")
    if lic_date:
        print(f"string date: {lic_date}")
        info_data['companies'][company_id]['license_pay_date'] = get_epoch_from_string(lic_date)
    if lic_amount:
        info_data['companies'][company_id]['license_pay_amount'] = lic_amount
    if lic_term:
        info_data['companies'][company_id]['license_term'] = lic_term
    if user_pass:
        info_data['users'][user_id]['password'] = user_pass
    if user_email:
        info_data['users'][user_id]['email'] = user_email
    if user_phone:
        info_data['users'][user_id]['phone'] = user_phone

    save_json_to_file_mtadmin(INFO_FILE, info_data)
    return_obj = json.dumps({'response': {'status': 'success'}})

    lock.release()
    return return_obj


@app.route('/customers/condo/retrieve_customer', methods=["POST"])
@login_required
def retrieve_customer_condo():
    lock.acquire()
    print(f"here in server_admin.retrieve_customer()")
    prefix = 'customer'
    json_obj = request.get_json()
    tenant = json_obj[prefix]['tenant']

    # read the INFO_FILE to update the info
    if not aws.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    customers = get_json_from_file(f"{INFO_FILE}")['config']

    if tenant not in customers:
        return_obj = json.dumps({'response': {'status': 'not_found'}})
        lock.release()
        return return_obj

    customer = customers[tenant]

    if 'admin_userid' in customer:
        users_repository.load_users(customer['domain'])
        user = users_repository.get_user_by_userid(customer['domain'], customer['admin_userid'])
        customer['admin_pass'] = user.password
        customer['admin_email'] = user.email
        customer['admin_phone'] = user.phone
    else:
        customer['admin_userid'] = ''
        customer['admin_pass'] = ''
        customer['admin_email'] = ''
        customer['admin_phone'] = ''

    lic_pay_date = get_string_from_epoch_format(customer['license_pay_date'], '%Y-%m-%d') if customer['license_pay_date'] else ''
    response = {
        'status': 'success',
        'admin_userid': customer['admin_userid'],
        'admin_pass': customer['admin_pass'],
        'admin_email': customer['admin_email'],
        'admin_phone': customer['admin_phone'],
        'license_pay_date': lic_pay_date,
        'license_pay_amount': customer['license_pay_amount'],
        'license_term': customer['license_term']
    }

    return_obj = json.dumps( {'response': response} )
    lock.release()
    return return_obj


@app.route('/customers/company/retrieve_customer', methods=["POST"])
@login_required
def retrieve_customer_company():
    lock.acquire()
    print(f"here in server_admin.retrieve_customer()")
    prefix = 'customer'
    json_obj = request.get_json()
    company_id = json_obj[prefix]['tenant']

    # read the INFO_FILE to update the info
    if not aws_mtadmin.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    customers = get_json_from_file_mtadmin(f"{INFO_FILE}")

    if company_id not in customers['companies']:
        return_obj = json.dumps({'response': {'status': 'not_found'}})
        lock.release()
        return return_obj

    customer = customers['companies'][company_id]

    users_list = customers['users_by_company'][company_id]['users']

    if len(users_list) > 0:
        user_id = users_list[0]
        customer['admin_userid'] = user_id
        customer['admin_pass'] = customers['users'][user_id]['password']
        customer['admin_email'] = customers['users'][user_id]['email']
        customer['admin_phone'] = customers['users'][user_id]['phone']
    else:
        customer['admin_userid'] = ''
        customer['admin_pass'] = ''
        customer['admin_email'] = ''
        customer['admin_phone'] = ''

    lic_pay_date = get_string_from_epoch_format(customer['license_pay_date'], '%Y-%m-%d') if customer['license_pay_date'] else ''
    response = {
        'status': 'success',
        'admin_userid': customer['admin_userid'],
        'admin_pass': customer['admin_pass'],
        'admin_email': customer['admin_email'],
        'admin_phone': customer['admin_phone'],
        'license_pay_date': lic_pay_date,
        'license_pay_amount': customer['license_pay_amount'],
        'license_term': customer['license_term']
    }

    return_obj = json.dumps( {'response': response} )
    lock.release()
    return return_obj


@app.route('/customers/condo/delete_customer', methods=["POST"])
@login_required
def delete_customer_condo():
    lock.acquire()
    print(f"here in delete_customer()")
    prefix = 'customer'
    json_obj = request.get_json()
    tenant = json_obj[prefix]['tenant']

    # read the INFO_FILE to update the info
    if not aws.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    customers = get_json_from_file(f"{INFO_FILE}")

    if tenant not in customers['config']:
        return_obj = json.dumps({'response': {'status': 'not_found'}})
        lock.release()
        return return_obj

    # delete customer
    del customers['config'][tenant]

    # write structure back to file
    save_json_to_file(INFO_FILE, customers)

    # now delete the tenant's folder under 'customers'
    aws.delete_folder(tenant)

    response = { 'status': 'success' }
    return_obj = json.dumps( {'response': response} )
    lock.release()
    return return_obj

@app.route('/customers/company/delete_customer', methods=["POST"])
@login_required
def delete_customer_company():
    lock.acquire()
    print(f"here in delete_customer_company()")
    prefix = 'customer'
    json_obj = request.get_json()
    company_id = json_obj[prefix]['tenant']

    # read the INFO_FILE to update the info
    if not aws_mtadmin.is_file_found(f"{INFO_FILE}"):
        return_obj = json.dumps({'response': {'status': 'error'}})
        lock.release()
        return return_obj

    customers = get_json_from_file(f"{INFO_FILE}")
    if company_id not in customers['companies']:
        return_obj = json.dumps({'response': {'status': 'not_found'}})
        lock.release()
        return return_obj

    # delete customer
    del customers['companies'][company_id]

    # delete all users linked to that company
    users = customers['users_by_company'][company_id]['users']
    for user_id in users:
        del customers['users'][user_id]
    del customers['users_by_company'][company_id]
    # write structure back to file
    save_json_to_file_mtadmin(INFO_FILE, customers)

    # now delete the tenant's folder under 'customers'
    aws_mtadmin.delete_folder(company_id)

    response = { 'status': 'success' }
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
    app_name = 'server_admin.py'
    print(f"app name: {app_name}")
    return app

'''
  host='0.0.0.0' means "accept connections from any client ip address".
'''
# def main():
#     app.run(host='0.0.0.0', port=8080, debug=False)
#
# if __name__ == '__main__':
#     main()
