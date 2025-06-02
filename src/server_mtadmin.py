
#----------------------------------------------------------------------------------------#
#                                                                                        #
#  Module responsible for registering new companies                                      #
#  Implements all routes that starts with "multi-condo"                                  #
#----------------------------------------------------------------------------------------#
import staticvars
import calendar
import json
import pytz

from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_babel import Babel, lazy_gettext, _

from threading import Lock

from server import reduce_image_enh, send_email_redmail, get_epoch_from_now, load_company_users
from datetime import timedelta, datetime

# these are import of variables
from server import config, users_repository_mtadmin, aws_mtadmin, COVER_PREF_WIDTH, COVER_PREF_HEIGHT, UNPROTECTED_FOLDER


INFO_FILE = "info.json"

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
            template_folder='templates/mtadmin'
           )

app.config['SECRET_KEY'] = config['flask_secret_key']
app.url_map.strict_slashes = False

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = u'Due to inactivity, you have been logged out. Please login again'
login_manager.login_message = 'Login is required to access the page you want'
login_manager.needs_refresh_message_category = 'info'

# define the lock object
lock = Lock()

def is_company_found(company):
    if not aws_mtadmin.is_file_found(f"{INFO_FILE}"):
        return False
    string_content = aws_mtadmin.read_text_obj(INFO_FILE)
    info_json = json.loads(string_content)
    if company in info_json['companies']:
        return True
    return False

# in company_data we return only data specific to that company
def get_company_data(company_id):
    if not aws_mtadmin.is_file_found(f"{INFO_FILE}"):
        print(f"get_company_data(): file not found: {INFO_FILE},  company: {company_id}")
        return None

    try:
        info = aws_mtadmin.read_text_obj(f"{INFO_FILE}")
        json_obj = json.loads(info)
        if company_id in json_obj['companies']:
            company_data = json_obj['companies'][company_id]
            #company_data['tenants'] = json_obj['tenants_by_company'][company_id]['tenants']
            company_data['is_authenticated'] = not current_user.is_anonymous
            return company_data
        else:
            return None
    except:
        print(f"get_company_data(): unable to get info for company: {company_id}, file {INFO_FILE}")
        return None

def get_user_id_and_company_id(user_internal_id):
    #logged_user = current_user.id
    ind = user_internal_id.find("@")
    company_id = user_internal_id[ind + 1:]
    user_id = user_internal_id[2:ind]
    return user_id, company_id

#-----------------------------------------------------------------------------------------------------
#     File related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/common/img/<filename>')
def static_image_files(filename):
    print(f"here in static_image_files(): filename: {filename}")
    file_obj = open(f"{app.static_folder}/img/{filename}", "rb")
    return Response(response=file_obj, status=200, mimetype="image/jpg")

@app.route('/<company>/branding/<filename>')
def custom_static_branding(company, filename):
    print(f"custom_static_branding(): tenant {company}, filename {filename}")
    file_obj = aws_mtadmin.read_binary_obj(f"{company}/{UNPROTECTED_FOLDER}/branding/{filename}")
    return Response(response=file_obj, status=200, mimetype="image/jpg")


#-----------------------------------------------------------------------------------------------------
#     Registration related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/')
def home_root():
    return redirect("multi-condo/registrar_portugues")

@app.route('/registrar_portugues')
def home_pt():
    lock.acquire()
    print("here in mtadmin.home_pt()")
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "pt"
    }
    lock.release()
    return render_template("registration_mtadmin.html", user_types=staticvars.user_types, info_data=info_data)


@app.route('/sobre_portugues')
def about_self_pt():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "pt"
    }
    lock.release()
    return render_template("about_mtadmin.html", info_data=info_data)


@app.route('/register_en')
def home_en():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "en"
    }
    lock.release()
    return render_template("registration_mtadmin.html", user_types=staticvars.user_types, info_data=info_data)


@app.route('/about_en')
def about_self_en():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "en"
    }
    lock.release()
    return render_template("about_mtadmin.html", info_data=info_data)


#----------------------------------------------------------------------------------------------
# All "multi-condo" related route pages
#----------------------------------------------------------------------------------------------
@app.route('/<company>', methods=['GET'])
def multi_condo_root(company):
    return redirect(f"/multi-condo/{company}/home")

@app.route('/<company>/home', methods=['GET'])
def multi_condo_home(company):
    lock.acquire()
    print(f"here in multi_condo_home()")

    if not is_company_found(company):
        lock.release()
        info_data = {'company_id': company}
        return render_template("company_not_found.html", info_data=info_data)

    if not current_user.is_authenticated:
        lock.release()
        return redirect(f"/multi-condo/{company}/login")

    if company != session['company_id']:
        user_id, company_id = get_user_id_and_company_id(current_user.id)
        info_data = {
            'user_id': user_id, 'company_id': company_id
        }
        lock.release()
        return render_template(f"already_logged_in.html", info_data=info_data)

    company_data = get_company_data(company)
    company_user_data = { 'user_id': company, 'company_id': company }
    company_data['loggedin-userdata'] = company_user_data
    lock.release()
    return render_template('home_mtadmin.html', info_data=company_data)

@app.route('/<company>/login', methods=['GET' , 'POST'])
def multi_condo_login(company):
    lock.acquire()
    # print(f"here in login_tenant(), {request.path}")

    if request.method == 'GET':
        if current_user.is_authenticated:
            next_page = request.args.get('next') if request.args.get('next') is not None else f'/multi-condo/{company}/home'
            lock.release()
            return redirect(next_page)
        else:
            lock.release()
            return render_template('login_mtadmin.html')

    # from here on down, it's a POST request
    if current_user.is_authenticated:
        next_page = request.args.get('next') if request.args.get('next') is not None else f'/multi-condo/{company}/home'
        lock.release()
        return redirect(next_page)

    # print(f"login_tenant(): current_user {current_user} is not authenticated")
    user_id = request.form['userid']
    password = request.form['password']
    load_company_users(company)

    print(f"loaded user: {user_id},  {users_repository_mtadmin.get_user_by_userid(user_id)}")
    registered_user = users_repository_mtadmin.get_user_by_userid(user_id)

    if registered_user is None:
        print(f"registered user is None")
        flash("Invalid userid or password")
        lock.release()
        return render_template("login_mtadmin.html")

    print(f"user: userid {registered_user.userid}   password: {registered_user.password}")
    print(f"tenants: {users_repository_mtadmin.get_tenants(user_id)}")

    if registered_user.password == password:
        print(f"password matches")
        registered_user.authenticated = True

        # invoke flask login_user
        login_user(registered_user)

        session['multi-condo'] = True
        session['user_id'] = user_id
        session['company_id'] = company
        session['language'] = users_repository_mtadmin.get_language()
        session['tenants'] = users_repository_mtadmin.get_tenants(user_id)
        print(f"current_user (just logged in): {current_user}")
        lock.release()
        return redirect(f"/multi-condo/{company}/home")
    else:
        #return abort(401)
        flash("Invalid userid or password")
        lock.release()
        return render_template("login_mtadmin.html")

@app.route('/<company>/logout', methods=['GET'])
def multi_condo_logout(company):
    lock.acquire()
    print(f"multi_condo_logout(): session: {session}")

    if not is_company_found(company):
        lock.release()
        return render_template("company_not_found.html", tenant=company)

    if not current_user.is_authenticated:
        lock.release()
        return redirect(f"/multi-condo/{company}/login")

    # from here on down we know the company is logged in
    if company != session['company_id']:
        user_id, company_id = get_user_id_and_company_id(current_user.id)
        info_data = {
            'user_id': user_id,
            'company_id': company
        }
        lock.release()
        return render_template("company_not_logged_in.html", info_data=info_data)

    # we need to gather some data to be shown in the logout.html view
    #info_data = prepare_info_data(company)

    # from here on down we know that a user is logged in
    print(f"to be logged out.. userid: {current_user.userid}    id: {current_user.id}")

    current_user.authenticated = False
    userid = current_user.userid  # we need to save the userid BEFORE invoking logout_user()
    logout_user()
    session['tenant'] = None
    session['language'] = None
    info_data = {'loggedin-userdata': { 'user_id': userid, 'company_id': company } }
    lock.release()
    return render_template("logout_mtadmin.html", info_data=info_data)


@app.route('/<company>/get_company_info')
@login_required
def get_company_info(company):
    lock.acquire()
    print(f"here in get_company_info()")

    if not is_company_found(company):
        lock.release()
        return render_template("company_not_found.html", company=company)

    company_data = get_company_data(company)
    lock.release()
    return json.dumps(company_data)

@app.route('/<company>/update_company_info', methods=["POST"])
@login_required
def update_company_info(company):
    lock.acquire()
    print(f"here in update_company_info()")

    if not is_company_found(company):
        lock.release()
        return render_template("company_not_found.html", company=company)

    json_req = request.get_json()
    info = json.loads(aws_mtadmin.read_text_obj(INFO_FILE))
    info['companies'][company]['email'] = json_req['request']['email']
    info['companies'][company]['phone'] = json_req['request']['phone']
    info['companies'][company]['company_name'] = json_req['request']['name']
    info['companies'][company]['address'] = json_req['request']['address']
    info['companies'][company]['number'] = json_req['request']['number']
    info['companies'][company]['complement'] = json_req['request']['complement']
    info['companies'][company]['zip'] = json_req['request']['zip']
    info['companies'][company]['city'] = json_req['request']['city']
    info['companies'][company]['state'] = json_req['request']['state']
    info['companies'][company]['country'] = json_req['request']['country']
    info['companies'][company]['language'] = json_req['request']['language']
    info['companies'][company]['last_update_date'] = get_epoch_from_now()
    string_content = json.dumps(info, indent=4, ensure_ascii=False)
    aws_mtadmin.upload_text_obj(f"{INFO_FILE}", string_content)
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj

@app.route('/<company>/upload_file', methods=['POST'])
@login_required
def multi_condo_upload(company):
    lock.acquire()
    print(f"here in multi_condo_upload(): {company}")

    if not is_company_found(company):
        lock.release()
        return render_template("company_not_found.html", tenant=company)

    uploaded_file = request.files['file']
    uploaded_file.stream.seek(0)
    img_bytes = uploaded_file.read()
    img_format, new_img_bytes = reduce_image_enh(img_bytes, COVER_PREF_WIDTH, COVER_PREF_HEIGHT)
    logo_name = "logo.jpg" if img_format == 'JPEG' else "logo.png"
    full_path = f"{company}/{UNPROTECTED_FOLDER}/branding/{logo_name}"
    aws_mtadmin.upload_binary_obj(full_path, new_img_bytes)
    print(f"full path: {full_path}")
    return_obj = json.dumps({'response': {'status': 'success'}})
    lock.release()
    return return_obj


@app.route('/check_company_id', methods=['POST'])
def check_company_id():
    lock.acquire()
    print("in check_company_id()")
    company_id = request.form['company_id'].lower()

    if is_company_found(company_id):
        return_obj = {'status': 'error', 'message': f"{company_id} already exists in our system"}
        ret_json = json.dumps(return_obj)
        lock.release()
        return ret_json

    return_obj = {'status': 'success', 'company_id': company_id}
    lock.release()
    return return_obj


@app.route('/register_company', methods=['POST'])
def register_company():
    lock.acquire()
    print("in register_company()")
    company_name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    pref_language = request.form['pref_language']
    company_id = request.form['company_id'].lower()
    address = request.form['address']
    address_number = request.form['address_number']
    address_complement = request.form['address_complement']
    zip = request.form['zip']
    city = request.form['city']
    state = request.form['state']
    country = request.form['country']
    invoke_origin = request.form['invoke_origin']

    if invoke_origin == 'web_api':
        api_key = request.form['api_key']
        if api_key != config['api_key']:
            return_obj = {'status': 'error', 'message': f"invalid API_KEY"}
            ret_json = json.dumps(return_obj)
            lock.release()
            return ret_json
        print(f"api_key validation passed")


    if is_company_found(company_id):
        return_obj = {'status': 'error', 'message': f"{company_id} already exists in our system"}
        ret_json = json.dumps(return_obj)
        print("condo already exists...returning")
        lock.release()
        return ret_json

    print(f"company {company_id} not found. We are creating it now....")

    #epoch_timestamp = calendar.timegm(datetime.now().timetuple())
    #timezone = pytz.timezone("America/New_York")
    #now_with_timezone = datetime.now(timezone)
    info = json.loads(aws_mtadmin.read_text_obj(f"{INFO_FILE}"))

    epoch_timestamp = get_epoch_from_now()
    company_info = {
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "address": address,
        "complement": address_complement,
        "number": address_number,
        "zip": zip,
        "city": city,
        "state": state,
        "country": country,
        "tenants": [],
        "last_update_date": None,
        "language": pref_language,
        "payment_link": "",
        "registration_date": None,
        "license_pay_date": None,
        "license_pay_amount": None,
        "license_date": None,
        "license_term": None,
        "origin": invoke_origin
    }

    info['companies'][company_id] = company_info

    # create a user associated with that company
    user_id = f"user_{company_id}"
    user_name = "Change this user name"
    user_email = email
    user_phone = phone
    user_last_update_date = None
    user_last_login = None
    user_pass = f"{epoch_timestamp}@{company_id}"
    user_data = {
        "name": user_name,
        "email": user_email,
        "phone": user_phone,
        "created_date": epoch_timestamp,
        "last_update_date": user_last_update_date,
        "last_login_date": user_last_login,
        "password": user_pass
    }

    info['users'][user_id] = user_data
    info['users_by_company'][company_id] = { "users": [user_id]}
    info['company_by_user'][user_id] = { "company": company_id}

    # update the info.json file
    string_content = json.dumps(info, indent=4, ensure_ascii=False)
    aws_mtadmin.upload_text_obj(f"{INFO_FILE}", string_content)

    # add the logo image
    logo_pic = open(f"{app.static_folder}/img/coml_building.png", "rb")
    aws_mtadmin.upload_binary_obj(f"{company_id}/uploadedfiles/unprotected/branding/logo.jpg", logo_pic.read())

    # email to let user know he's registered
    if pref_language == 'pt':
        body = f"Parabéns!\n\nVocê registrou com sucesso {company_id} no CondoSpace App. Abaixo estão as credenciais de login:\n\n"
        body += f"O endereço de website da gestora: https://condospace.app/multi-condo/{company_id}\n"
        body += f"Usuário Admin: {user_id}\n"
        body += f"Senha do Admin: {user_pass}\n"
        subject = 'Registro de Gestora no CondoSpace App'
    else:
        body = f"Congratulations!\n\nYou successfully registered company {company_id} at CondoSpace App. Below are your credentials:\n\n"
        body += f"Your company website address: https://condospace.app/multi-condo/{company_id}\n"
        body += f"Your Admin Id: {user_id}\n"
        body += f"Your Admin Password: {user_pass}\n"
        subject = 'CondoSpace Registration Form'

    if invoke_origin == 'web_gui':
        send_email_redmail(user_email, subject, body)
        send_email_redmail(config['CONTACT_TARGET_EMAIL'], subject, body)
        print(f"just sent email to {user_email}, epoch timestamp: {epoch_timestamp}")

    return_obj = {'status': 'success', 'company_id': company_id, 'user_id': user_id, 'password': user_pass}
    lock.release()
    return return_obj

# this function is invoked by the Condo Registration module
# to link a condo to a company when the condo is being registered
# by such a company
def update_company_data(company_id, tenant_id):
    info = json.loads(aws_mtadmin.read_text_obj(f"{INFO_FILE}"))
    if company_id in info['companies']:
        info['companies'][company_id]['tenants'].append(tenant_id)
    else:
        print(f"Company Id not found in the INFO_FILE")
        return False

    # update the info.json file
    string_content = json.dumps(info, indent=4, ensure_ascii=False)
    aws_mtadmin.upload_text_obj(f"{INFO_FILE}", string_content)
    return True

#-----------------------------------------------------------------------------------------------------
#     Security related routines
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
def load_user(user_internal_id):
    print(f"here in mtadmin load_user(): {user_internal_id}")
    # ind = user_internal_id.find("@")
    # company_id = user_internal_id[ind + 1:]
    # user_id = user_internal_id[2:ind]

    user_id, company_id = get_user_id_and_company_id(user_internal_id)
    load_company_users(company_id)
    print(f"all tenants: {users_repository_mtadmin.get_tenants(user_id)}")
    user = users_repository_mtadmin.get_user_by_id(user_internal_id)
    if user is None:
        ret_user = None
    else:
        ret_user = user

    print(f"user id {user_internal_id} found!")
    return ret_user

# This is invoked by Babel
def get_locale():
    print(f"request.path: {request.path}")
    if request.path in ('/registrar_portugues', '/sobre_portugues'):
        return "pt"
    if request.path in ('/register_en', '/about_en'):
        return "en"
    if current_user.is_authenticated:
        print(f"in get_locale(): user is authenticated. language: {session['language']}")
        return session['language']
    return "en"

def create_app():
    app_name = 'server_mtadmin.py'
    print(f"app name: {app_name}")
    return app

# this call cannot be inside main() because this will run with gunicorn in PROD
babel = Babel(app, locale_selector=get_locale)
_ = lazy_gettext


'''
  host='0.0.0.0' means "accept connections from any client ip address".
'''
# def main():
#     app.run(host='0.0.0.0', port=8080, debug=False)
#
# if __name__ == '__main__':
#     main()
