
#----------------------------------------------------------------------------------------#
#                                                                                        #
#  Module responsible for registering new customers                                      #
#                                                                                        #
#----------------------------------------------------------------------------------------#
import staticvars
import calendar
import json
import pytz

from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_babel import Babel, lazy_gettext, _

from threading import Lock
from aws import AWS

from users import UsersRepository
from users_adm import UsersRepository as UsersAdmRepository
from datetime import timedelta, datetime
from server import is_tenant_found
from server import get_lat_long
from server import save_announc_common
from server import get_json_from_file_no_tenant
from server import reduce_image_enh
from server import send_email_redmail
from server import save_json_to_file
from server import save_json_to_file_no_tenant
from server import get_info_data
from server import get_epoch_from_now
from server import RESIDENTS_FILE
from server import LINKS_FILE
from server import INFO_FILE
from server import CONFIG_FILE
from server import BUCKET_PREFIX
from server import COVER_PREF_WIDTH, COVER_PREF_HEIGHT
from server_mtadmin import update_company_data


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
            template_folder='templates/regis'
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


#-----------------------------------------------------------------------------------------------------
#     File related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/common/img/<filename>')
def static_image_files(filename):
    file_obj = open(f"{app.static_folder}/img/{filename}", "rb")
    return Response(response=file_obj, status=200, mimetype="image/jpg")


#-----------------------------------------------------------------------------------------------------
#     Registration related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/')
def home_root():
    return redirect("regis/registrar_portugues")

@app.route('/root')
def home():
    return redirect("regis/registrar_portugues")

@app.route('/registrar_portugues')
def home_pt():
    lock.acquire()
    print("here in regis.home_pt()")
    company_id = request.args.get('company_id', default='', type=str)
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "pt",
        "company_id": company_id
    }
    lock.release()
    return render_template("home_root.html", user_types=staticvars.user_types, info_data=info_data)

@app.route('/sobre_portugues')
def about_self_pt():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "pt"
    }
    lock.release()
    return render_template("about_root.html", info_data=info_data)


@app.route('/register_en')
def home_en():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "en"
    }
    lock.release()
    return render_template("home_root.html", user_types=staticvars.user_types, info_data=info_data)


@app.route('/about_en')
def about_self_en():
    lock.acquire()
    info_data = {
        "condo_name": "CondoSpace App",
        "language": "en"
    }
    lock.release()
    return render_template("about_root.html", info_data=info_data)


@app.route('/check_condo_id', methods=['POST'])
def check_condo_id():
    lock.acquire()
    print("in check_condo_id()")
    condo_id = request.form['condo_id'].lower()

    if is_tenant_found(condo_id):
        return_obj = {'status': 'error', 'message': f"{condo_id} already exists in our system"}
        ret_json = json.dumps(return_obj)
        lock.release()
        return ret_json

    return_obj = {'status': 'success', 'condo_id': condo_id}
    lock.release()
    return return_obj


@app.route('/register_condo', methods=['POST'])
def register_condo():
    lock.acquire()
    print("in register_condo()")
    company_id = request.form['company_id']
    user_full_name = request.form['name']
    user_email = request.form['email']
    user_phone = request.form['phone']
    pref_language = request.form['pref_language']
    condo_id = request.form['condo_id'].lower()
    condo_name = request.form['condo_name']
    condo_tagline = request.form['condo_tagline']
    condo_address = request.form['condo_address']
    condo_address_number = request.form['condo_address_number']
    condo_zip = request.form['condo_zip']
    condo_city = request.form['condo_city']
    condo_state = request.form['condo_state']
    condo_country = request.form['condo_country']
    use_default_img = True if request.form['use_default_img'] == 'yes' else False
    invoke_origin = request.form['invoke_origin']

    if invoke_origin == 'web_api':
        api_key = request.form['api_key']
        if api_key != config['api_key']:
            return_obj = {'status': 'error', 'message': f"invalid API_KEY"}
            ret_json = json.dumps(return_obj)
            lock.release()
            return ret_json
        print(f"api_key validation passed")

    if invoke_origin == 'web_api':
        userid = request.form['user']
    else:
        userid = user_full_name.strip().lower()
        if userid.find(' ') != -1:
            ind = userid.find(' ')
            userid = f"{userid[:ind]}_{condo_id}"
        else:
            userid = f"{userid}_{condo_id}"

    if is_tenant_found(condo_id):
        return_obj = {'status': 'error', 'message': f"{condo_id} already exists in our system"}
        ret_json = json.dumps(return_obj)
        print("condo already exists...returning")
        lock.release()
        return ret_json

    print(f"tenant {condo_id} not found. We are creating it now....")

    if invoke_origin == 'web_gui':
        lat, long = get_lat_long(f"{condo_address}, {condo_address_number}, {condo_city}, {condo_state}")
        if lat is None or long is None:
            lat = -22.9561
            long = -46.5473
    else:
        lat = request.form['lat']
        long = request.form['long']

    #epoch_timestamp = calendar.timegm(datetime.now().timetuple())
    #timezone = pytz.timezone("America/New_York")
    #now_with_timezone = datetime.now(timezone)
    epoch_timestamp = get_epoch_from_now()
    epoch_date_time = datetime.fromtimestamp(epoch_timestamp)
    print(f"epoch_timestamp: [{epoch_timestamp}]  Converted Datetime back: {epoch_date_time}")

    if pref_language == 'pt':
        pix_key = "12345678"
        fine_title = "Notificação de Multa Condominial"
        fine_template = """
Prezado(a) {name},

Esta é uma notificação de que o senhor(a) tem uma multa por {descr},
a ser paga no valor de {amount}, com data de vencimento em {due_date}.

O valor pode ser pago via PIX cuja chave é {pix}.

Muito obrigado.

Administração, {condo_name}.
"""
        pay_pix_key = "12345678"
        pay_title = "Notificação de Cobrança"
        pay_template = """
Prezado(a) {name},

Esta é uma notificação de que o senhor(a) tem uma cobrança por {descr},
emitida em {issue_date}, cujo número de identificação no sistema é {payment_ref},      
a ser paga no valor de {amount}, com data de vencimento em {due_date}.

O valor desta cobrança pode ser pago via PIX cuja chave recebedora é {pix}.

Muito obrigado.

Administração, {condo_name}."""
    elif pref_language == 'en':
        pix_key = ""
        fine_title = "Notification of Condominium Fine"
        fine_template = """
Dear {name},
This is a notification that you have been issued a fine in the amount of {amount},
with due date on {due_date}.

The amount may be paid with credit card or via check.

Thank you.

Board of Directors of {condo_name}.
"""
        pay_pix_key = ""
        pay_title = "Payment Request"
        pay_template = """
Dear {name},
This is a notification that you have been requested to make a payment in the amount of {amount},
with due date on {due_date}.

The amount may be paid with credit card or via check.

Thank you.

Board of Directors of {condo_name}.
"""
    else:
        pix_key = ''
        fine_title = ''
        fine_template = ''
        pay_pix_key = ''
        pay_title = ''
        pay_template = ''

    admin_pass = f"{condo_id}@{epoch_timestamp}"

    condo_info = {
        "admin_name": user_full_name,
        "admin_email": user_email,
        "admin_userid": userid,
        "admin_pass": admin_pass,
        "payment_link": "",
        "license_pay_date": None,
        "license_pay_amount": None,
        "license_date": None,
        "license_term": None,
        'registration_date': epoch_timestamp,
        'default_home_pic': use_default_img,
        "language": pref_language,
        "address": condo_address,
        "address_number": condo_address_number,
        "zip": condo_zip,
        "census_forms_pdf_date": "06-Sep-2024",
        "condo_city": condo_city,
        "condo_state": condo_state,
        "condo_country": condo_country,
        "condo_name": condo_name,
        "domain": condo_id,
        "tagline": condo_tagline,
        "geo": {"lat": lat, "long": long},
        "home_message": {
            "title": "Olá Pessoal.",
            "lines": [
                f"Bem-vindo ao lindo {condo_name} em {condo_city}, {condo_state}.",
                "Nós mal podemos esperar ver você aqui e, ao mesmo tempo, te fornecer informações muito úteis.",
                "Se você já for um residente aqui, documentos e informações estão a apenas alguns clicks."
            ]
        },
        "about_message": {
            "title": "Tudo Sobre Nós.",
            "lines": [
                f"Nós somos uma pequena e vibrante associação localizada em {condo_city}, {condo_state}.",
                "A nossa região proporciona o que há de melhor em qualidade de vida e segurança.",
                "Estamos localizados numa área nobre da cidade, rodeados pelo que há de melhor em gastronomia e compras de nível internacional, além de fácil acesso por ótimas estradas da região."
            ]
        },
        'pix_key': pix_key,
        'fine_title': fine_title,
        'fine_template': fine_template,
        'pay_pix_key': pay_pix_key,
        'pay_title': pay_title,
        'pay_template': pay_template,
        'origin': 'api' if invoke_origin == 'web_api' else 'cust',
        'last_login_date': epoch_timestamp
    }

    initial_resident = {
        "residents": [
            {
                "unit": 0,
                "userid": f"{userid}",
                "password": f"{admin_pass}",
                "name": f"{user_full_name}",
                "email": f"{user_email}",
                "startdt": {
                    "month": 1,
                    "year": 2025
                },
                "phone": f"{user_phone}",
                "type": 0,
                "ownername": "",
                "owneremail": "",
                "ownerphone": "",
                "owneraddress": "",
                "isrental": False,
                "emerg_name": "",
                "emerg_email": "",
                "emerg_phone": "",
                "emerg_has_key": False,
                "occupants": [
                    {
                        "name": "",
                        "email": "",
                        "cc": False,
                        "phone": "",
                        "has_key": False
                    },
                    {
                        "name": "",
                        "email": "",
                        "cc": False,
                        "phone": "",
                        "has_key": False
                    },
                    {
                        "name": "",
                        "email": "",
                        "cc": False,
                        "phone": "",
                        "has_key": False
                    },
                    {
                        "name": "",
                        "email": "",
                        "cc": False,
                        "phone": "",
                        "has_key": False
                    },
                    {
                        "name": "",
                        "email": "",
                        "cc": False,
                        "phone": "",
                        "has_key": False
                    }
                ],
                "oxygen_equipment": False,
                "limited_mobility": False,
                "routine_visits": False,
                "has_pet": True,
                "bike_count": 0,
                "insurance_carrier": "",
                "valve_type": 0,
                "no_vehicles": True,
                "vehicles": [
                    {
                        "make_model": "",
                        "plate": "",
                        "color": "",
                        "year": None
                    },
                    {
                        "make_model": "",
                        "plate": "",
                        "color": "",
                        "year": None
                    }
                ],
                "last_update_date": "",
                "notes": ""
            }]
    }

    initial_links = {"links": {}}
    save_json_to_file(condo_id, RESIDENTS_FILE, initial_resident)
    save_json_to_file(condo_id, LINKS_FILE, initial_links)

    if pref_language == 'pt':
        announc_text = f"{condo_name} estabeleceu presença online."
    else:
        announc_text = f"{condo_name} established online presence."

    save_announc_common(condo_id, userid, announc_text, None, None)

    # read the INFO_FILE to add a condo to it
    if aws.is_file_found(f"{INFO_FILE}"):
        info_data = get_json_from_file_no_tenant(f"{INFO_FILE}")
        info_data['config'][condo_id] = condo_info
    else:
        info_data = {'config': {condo_id: condo_info}}

    save_json_to_file_no_tenant(INFO_FILE, info_data)

    if use_default_img:
        home_pic = open(f"{app.static_folder}/img/branding/home.jpg", "rb")
        logo_pic = open(f"{app.static_folder}/img/branding/logo.jpg", "rb")
        aws.upload_binary_obj(f"{condo_id}/uploadedfiles/unprotected/branding/home.jpg", home_pic.read())
        aws.upload_binary_obj(f"{condo_id}/uploadedfiles/unprotected/branding/logo.jpg", logo_pic.read())
    else:
        home_pic = request.files['home_pic']
        home_pic.stream.seek(0)
        img_bytes = home_pic.read()
        aws.upload_binary_obj(f"{condo_id}/uploadedfiles/unprotected/branding/home.jpg", img_bytes)
        _, img_bytes = reduce_image_enh(img_bytes, COVER_PREF_WIDTH, COVER_PREF_HEIGHT)
        aws.upload_binary_obj(f"{condo_id}/uploadedfiles/unprotected/branding/logo.jpg", img_bytes)

    # email to let user know he's registered
    if pref_language == 'pt':
        body = f"Parabéns!\n\nVocê registrou com sucesso {condo_name} no CondoSpace App. Abaixo estão as credenciais de login:\n\n"
        body += f"O endereço de website do condomínio: https://condospace.app/{condo_id}\n"
        body += f"Usuário Admin: {userid}\n"
        body += f"Senha do Admin: {admin_pass}\n"
        subject = 'Registro de Condomínio no CondoSpace App'
    else:
        body = f"Congratulations!\n\nYou successfully registered {condo_name} at CondoSpace App. Below are your credentials:\n\n"
        body += f"Your condo website address: https://condospace.app/{condo_id}\n"
        body += f"Your Admin Id: {userid}\n"
        body += f"Your Admin Password: {admin_pass}\n"
        subject = 'CondoSpace Registration Form'

    if company_id:
        print(f"company_id {company_id}")
        success = update_company_data(company_id, condo_id)
        if not success:
            print(f"Error trying to update the company in the INFO_FILE")
        else:
            pass
    else:
        print(f"No company is involved in this registration")

    if invoke_origin == 'web_gui':
        send_email_redmail(user_email, subject, body)
        send_email_redmail(config['CONTACT_TARGET_EMAIL'], subject, body)
        print(f"just sent email to {user_email}, epoch timestamp: {epoch_timestamp}")

    return_obj = {'status': 'success', 'condo_id': condo_id, 'user_id': userid, 'password': admin_pass}
    lock.release()
    return return_obj


#-----------------------------------------------------------------------------------------------------
#     Login/Logout related routines
#-----------------------------------------------------------------------------------------------------
@app.route('/login', methods=['GET' , 'POST'])
def login():
    lock.acquire()
    if request.method == 'GET':
        if current_user.is_authenticated:
            # print(f"login_tenant(): there is a user already logged in: {current_user.id}")
            next_page = request.args.get('next') if request.args.get('next') is not None else '/registrar_portugues'
            lock.release()
            return redirect(next_page)
        else:
            info_data = get_info_data('adm')
            lock.release()
            return render_template('login.html', info_data=info_data)

    # from here on down, it's a POST request
    if current_user.is_authenticated:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/registrar_portugues'
        lock.release()
        return redirect(next_page)

    userid = request.form['userid']
    password = request.form['password']
    load_users('adm')
    registered_user = users_adm_repository.get_user_by_userid('adm', userid)

    if registered_user.password == password:
        next_page = request.args.get('next') if request.args.get('next') is not None else '/registrar_portugues'
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


@app.route('/logout')
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

# This is invoked by Babel
def get_locale():
    print(f"request.path: {request.path}")
    if request.path in ('/registrar_portugues', '/sobre_portugues'):
        return "pt"
    if request.path in ('/register_en', '/about_en'):
        return "en"
    return "en"

def create_app():
    app_name = 'server_regis.py'
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
