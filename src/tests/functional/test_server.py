
"""
   This program should run from the root folder "condospace".
   Example:
       pytest src/tests/functional/test_server.py

   To run a single test:
       pytest src/tests/functional/test_server.py::test_insert_verify_delete_announc

   To run tests showing print statements:
       pytest --capture=no src/tests/functional/test_server.py::test_insert_verify_delete_announc
"""

from importmonkey import add_path
add_path("/home/joe/Documents/test-servers/condospace/src")  # relative to current __file__


from server import create_app  # Replace my_app with your application's import
from aws import AWS
from users import UsersRepository
import os
import requests


condo_id = "edificiorivera"
condo_user = "super_adm"
password = "edificiorivera@1745321771"

# condo_id = "edificioalfa"
# condo_user = "super_adm"
# password = "edificioalfa@1745321775"


home_endpoint = f"http://localhost:5000/{condo_id}/home"
announcs_endpoint = f"http://localhost:5000/{condo_id}/announcs"
docs_endpoint = f"http://localhost:5000/{condo_id}/docs"
pics_endpoint = f"http://localhost:5000/{condo_id}/pics"
get_resident_endpoint = f"http://localhost:5000/{condo_id}/getresident"
listings_endpoint = f"http://localhost:5000/{condo_id}/listings"
single_listing_endpoint = f"http://localhost:5000/{condo_id}/listing"
about_endpoint = f"http://localhost:5000/{condo_id}/about"
login_endpoint = f"http://localhost:5000/{condo_id}/login"

ANNOUNCEMENT_TEXT = "This is a big announcement for testing"
AMENITY_DESCR = "Football Society Court"


def test_all_high_level_menu_options():
    with requests.Session() as test_client:
        exec_test_home_page(test_client)
        exec_test_announcs(test_client)
        exec_test_docs(test_client)
        exec_test_pics(test_client)
        exec_test_listing(test_client)
        exec_test_about(test_client)
        exec_test_login(test_client)


def test_get_resident_unauthenticated():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        json_obj = {"request": {'type': 'user', 'tenant': 'edificioalfa', 'id': 'super_adm'}}
        response = test_client.post("http://localhost:5000/edificioalfa/getresident", json=json_obj)
        assert response.status_code == 302  # 302 means the server redirected to another page, in this case '/login'
        returned_content = response.text
        assert "You should be redirected" in returned_content


def test_get_resident_authenticated():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        # we need to login first
        status = login(test_client,"edificioalfa", "super_adm", "edificioalfa@1745321775")
        # if login is successful, the http status will be 200
        if status == 200:
            json_obj = {"request": {'type': 'user', 'tenant': 'edificioalfa', 'id': 'super_adm'}}
            response = test_client.post("http://localhost:5000/edificioalfa/getresident", json=json_obj)
            assert response.status_code == 200
            assert response.content_type == "application/json"
            json_resp = response.get_json()   # this only works if th mime type is "application/json"
            assert json_resp['response']['resident']['userid'] == 'super_adm'
            assert json_resp['response']['resident']['password'] == 'edificioalfa@1745321775'
            assert json_resp['response']['resident']['name'] == 'Super Administrador'

def test_get_resident_not_found():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        # we need to login first
        status = login(test_client,"edificioalfa", "super_adm", "edificioalfa@1745321775")
        # if login is successful, the http status will be 200
        if status == 200:
            json_obj = {"request": {'type': 'user', 'tenant': 'edificioalfa', 'id': 'super_abc'}}
            response = test_client.post("http://localhost:5000/edificioalfa/getresident", json=json_obj)
            assert response.status_code == 200
            assert response.content_type == "application/json"
            json_resp = response.get_json()
            assert json_resp['response']['status'] == 'not_found'

def test_get_resident_tenant_doesnt_match():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        # we need to log in first
        status = login(test_client,"edificioalfa", "super_adm", "edificioalfa@1745321775")
        # if login is successful, the http status will be 200
        if status == 200:
            json_obj = {"request": {'type': 'user', 'tenant': 'edificiblablabla', 'id': 'super_abc'}}
            response = test_client.post("http://localhost:5000/edificioalfa/getresident", json=json_obj)
            assert response.status_code == 200
            assert response.content_type == "application/json"
            json_resp = response.get_json()
            assert json_resp['response']['status'] == 'error'
            assert json_resp['response']['message'] == "tenant in the url doesn't match the one in payload"

def test_all_menu_authenticated(setup_and_teardown):
    test_client = setup_and_teardown
    exec_test_home_page(test_client)
    exec_test_announcs(test_client)
    exec_test_docs(test_client)
    exec_test_pics(test_client)
    exec_test_about(test_client)
    exec_test_listing(test_client)
    exec_test_login_redirect(test_client)
    exec_test_logged_in_menu(test_client)

def test_insert_modify_delete_resident(setup_and_teardown):
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    test_client = setup_and_teardown

    # add a resident to the database
    create_resident(test_client, tenant, user_id)

    # now read it back from the database
    json_obj = {"request": {'type': 'user', 'tenant': tenant, 'id': user_id}}
    response = test_client.post(f"http://localhost:5000/{tenant}/getresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    assert json_resp['response']['resident']['userid'] == user_id
    assert json_resp['response']['resident']['name'] == 'Joe Silva'
    assert json_resp['response']['resident']['email'] == 'joe@gmail.com'
    assert json_resp['response']['resident']['notes'] == 'Notes for AptoB101'

    # now modify the resident we just inserted
    json_insert = create_resident_json(tenant, user_id)
    json_insert['resident']['password'] = '987654321'
    json_insert['resident']['name'] = 'Another Name'
    json_insert['resident']['email'] = 'something@gmail.com'
    json_insert['resident']['phone'] = '(11) 98765-7855'
    json_insert['resident']['last_update_date'] = '2025-01-26' # this is required when modifying resident's data
    response = test_client.post(f"http://localhost:5000/{tenant}/saveresident", json=json_insert)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

    # now read it back from the database
    json_obj = {"request": {'type': 'user', 'tenant': tenant, 'id': user_id}}
    response = test_client.post(f"http://localhost:5000/{tenant}/getresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    assert json_resp['response']['resident']['userid'] == user_id
    assert json_resp['response']['resident']['password'] == '987654321'
    assert json_resp['response']['resident']['name'] == 'Another Name'
    assert json_resp['response']['resident']['email'] == 'something@gmail.com'
    assert json_resp['response']['resident']['phone'] == '(11) 98765-7855'
    assert json_resp['response']['resident']['notes'] == 'Notes for AptoB101' # this hasn't changed

    # now delete the resident we just inserted
    # todo: url needs to be changed to include tenant; field 'value' needs to be changed to 'user_id'
    json_obj = {"resident": {'type': 'user', 'tenant': tenant, 'value': user_id}}
    response = test_client.post(f"http://localhost:5000/deleteresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

    # now confirm the deletion of the resident from the database
    json_obj = {"request": {'type': 'user', 'tenant': tenant, 'id': user_id}}
    response = test_client.post(f"http://localhost:5000/{tenant}/getresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'not_found'


def test_insert_verify_delete_amenity(setup_and_teardown):
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    test_client = setup_and_teardown

    # add a resident to the database
    create_resident(test_client, tenant, user_id)

    # create amenity
    amenity_id = create_amenity(test_client, tenant, user_id)

    # verify amenity
    verify_amenity(test_client, tenant, user_id)

    # delete amenity
    delete_amenity(test_client, tenant, amenity_id)

    # delete a resident from the database
    delete_resident(test_client, tenant, user_id)


def test_insert_verify_delete_reservation(setup_and_teardown):
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    test_client = setup_and_teardown

    # add a resident to the database
    create_resident(test_client, tenant, user_id)

    # create amenity
    amenity_id = create_amenity(test_client, tenant, user_id)

    # add a reservation
    json_reservation = {
        "reservation": {
            "tenant": tenant,
            "admin_id": "super_adm",
            "user_id": user_id,
            "amenity_id": 0,   # we assume that this amenity_id is in the system
            "date": {"y": 2025, "m": 3, "d": 23},
            "time_from": {"h":  14, "m":  0},
            "time_to": {"h":  15, "m":  0},
            "send_email": "false"
        }
    }

    response = test_client.post(f"http://localhost:5000/{tenant}/make_reservation", json=json_reservation)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    rsv_id = json_resp['response']['rsv_id']
    print(f"rsv_id: {rsv_id}")

    # delete the newly created reservation
    json_obj = {"reservation": {'tenant': tenant, 'user_id': user_id, "rsv_id": str(rsv_id)}}
    response = test_client.post(f"http://localhost:5000/{tenant}/delete_reservation", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

    # now delete the newly inserted resident from the database
    # delete a resident from the database
    delete_resident(test_client, tenant, user_id)

    # delete amenity
    delete_amenity(test_client, tenant, amenity_id)


# Here we use the setup_and_teardown fixture defined in conftest.py
# The login and logout process is automatically executed by setup_and_teardown()
def test_insert_verify_delete_fine(setup_and_teardown):
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    test_client = setup_and_teardown

    # add a resident to the database
    create_resident(test_client, tenant, user_id)

    # insert a fine
    fine_dict = {
        "tenant": tenant,
        "user_id": user_id,
        "name": "John Wicket",
        "email": "joesilva01862@gmail.com",
        "phone": "(11) 96711-6743",
        "amount": "120.50",  # todo: can this be an integer in cents?
        "descr": "fine for rule violation",
        "due_date": {"y": 2025, "m": 3, "d": 23},
        "charge_type": "fine"
    }

    # create a fine
    fine_id = create_fine(test_client, tenant, fine_dict)

    # create a payment
    pay_id = create_payment(test_client, tenant, fine_dict)

    # read the fine back
    verify_fine(test_client, tenant, fine_id, fine_dict)

    # delete the fine
    delete_fine(test_client, tenant, user_id, fine_id)

    # delete the payment
    delete_fine(test_client, tenant, user_id, pay_id)

    # delete the resident created for this test
    delete_resident(test_client, tenant, user_id)


# Here we use the setup_and_teardown fixture defined in conftest.py
# The login and logout process is automatically executed by setup_and_teardown()
def test_insert_verify_delete_announc(app, setup_and_teardown):
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    print(f"current directory: {os.getcwd()}")
    test_client = setup_and_teardown

    # insert an announcement
    announc_id = create_announc(test_client, tenant, user_id)

    # verify announcement creation
    verify_announc(test_client, tenant, user_id)

    # delete announcement
    delete_announc(test_client, tenant, user_id, announc_id)


#-----------------------------------------------------------------------------------
#  supporting functions
#-----------------------------------------------------------------------------------
def login_using_client(client, tenant, login_data):
    login_response = client.post(f'http://localhost:5000/{tenant}/login', data=login_data)
    if login_response.status_code == 302:  # Check for redirect
        print(f"Redirection at login should never happen")
        return False
    return True

def create_amenity(client, tenant, user_id):
    json_amenity = {
        "tenant": tenant,
        "created_by": user_id,
        "descr": AMENITY_DESCR,
        "use_default_img": "yes",
        "paid_amenity": "false",
        "send_email": "false",
        "default_img_name": "/common/img/amenity_barbecue_grill.jpg"
    }
    response = client.post(f"http://localhost:5000/{tenant}/save_amenity", data=json_amenity)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    amenity_id = json_resp['response']['amenity_id']
    print(f"amenity_id: {amenity_id}")
    return amenity_id

def verify_amenity(client, tenant, user_id):
    response = client.get(f"http://localhost:5000/{tenant}/reservations")
    assert response.status_code == 200
    returned_content = response.text
    assert tenant in returned_content
    assert AMENITY_DESCR in returned_content

def delete_amenity(client, tenant, amenity_id):
    json_obj = {"amenity": {'tenant': tenant, "amenity_id": str(amenity_id)}}
    response = client.post(f"http://localhost:5000/{tenant}/delete_amenity", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

def create_announc(client, tenant, user_id):
    file_name = "src/tests/files/Produto_CondoSpace.pdf"
    bin_file = open(file_name, "rb") # rb is required because it's a binary file
    json_announc = {
        "tenant": tenant,
        "created_by": user_id,
        "text": ANNOUNCEMENT_TEXT,
        "attach_file_name": bin_file.name
    }
    files = { 'attach_file': bin_file }  # this structure needs to be sent separately
    response = client.post(f"http://localhost:5000/{tenant}/save_announc", files=files, data=json_announc)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    bin_file.close()
    return json_resp['response']['announc_id']

def verify_announc(client, tenant, user_id):
    response = client.get(f"http://localhost:5000/{tenant}/announcs")
    assert response.status_code == 200
    returned_content = response.text
    assert tenant in returned_content
    assert ANNOUNCEMENT_TEXT in returned_content

def delete_announc(client, tenant, user_id, announc_id):
    json_obj = {"announc": {'tenant': tenant, "user_id": user_id, "announc_id": str(announc_id)}}
    response = client.post(f"http://localhost:5000/{tenant}/delete_announc", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

def create_fine(client, tenant, fine_dict):
    response = client.post(f"http://localhost:5000/{tenant}/savefine", json={"payment": fine_dict})
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'
    fine_id = json_resp['response']['fine_id']
    return fine_id

def create_payment(client, tenant, fine_dict):
    fine_dict['charge_type'] = "pay"
    payment_id = create_fine(client, tenant, fine_dict) # fines and payments are created by the same endpoint
    return payment_id

def verify_fine(client, tenant, fine_id, fine_dict):
    response = client.get(f"http://localhost:5000/{tenant}/fines")
    assert response.status_code == 200
    returned_content = response.text
    assert fine_dict['user_id'] in returned_content
    assert fine_dict['name'] in returned_content
    assert fine_dict['email'] in returned_content
    assert fine_dict['descr'] in returned_content
    assert fine_dict['amount'] in returned_content


def delete_fine(client, tenant, user_id, fine_id):
    json_obj = {"fine": {'tenant': tenant, "user_id": user_id, "fine_id": str(fine_id)}}
    response = client.post(f"http://localhost:5000/{tenant}/deletefine", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'


def create_resident(client, tenant, user_id):
    # check to be sure that this resident is not found in the database
    json_obj = {"request": {'type': 'user', 'tenant': tenant, 'id': user_id}}
    response = client.post(f"http://localhost:5000/{tenant}/getresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'not_found'

    # add a resident to the database
    json_insert = create_resident_json(tenant, user_id)
    response = client.post(f"http://localhost:5000/{tenant}/saveresident", json=json_insert)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'

def delete_resident(client, tenant, user_id):
    # todo: url needs to be changed to include tenant; field 'value' needs to be changed to 'user_id'
    json_obj = {"resident": {'type': 'user', 'tenant': tenant, 'value': user_id}}
    response = client.post(f"http://localhost:5000/deleteresident", json=json_obj)
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp['response']['status'] == 'success'


def create_resident_json(tenant, user_id):
    # add a resident to the database
    resident_json = {
        "resident": {
            "tenant": tenant,
            "userid": user_id,
            "password": "test@rivera",
            "name": "Joe Silva",
            "email": "joe@gmail.com",
            "startdt": "",
            "phone": "123-5678",
            "type": 3,
            "ownername": "",
            "owneremail": "",
            "ownerphone": "",
            "owneraddress": "",
            "isrental": "",
            "emerg_name": "",
            "emerg_email": "",
            "emerg_phone": "",
            "emerg_has_key": "",
            "occupants": "",
            "oxygen_equipment": "",
            "limited_mobility": "",
            "routine_visits": "",
            "has_pet": "",
            "bike_count": "",
            "insurance_carrier": "",
            "valve_type": "",
            "no_vehicles": "",
            "vehicles": "",
            "notes": "Notes for AptoB101"
        }
    }
    return resident_json

def exec_test_home_page(test_client):
    response = test_client.get(home_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Início" in returned_content
    assert "Condominio do Edificio Rivera" in returned_content

def exec_test_announcs(test_client):
    response = test_client.get(announcs_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Anúncios" in returned_content

def exec_test_docs(test_client):
    response = test_client.get(docs_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Documentos" in returned_content

def exec_test_pics(test_client):
    response = test_client.get(pics_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Áreas Comuns do Condomínio" in returned_content
    assert "Eventos" in returned_content

def exec_test_about(test_client):
    response = test_client.get(about_endpoint)
    assert response.status_code == 200
    returned_content = response.text  #data.decode('utf-8')
    assert "Sobre" in returned_content
    assert "Versão e Data do Software" in returned_content

def exec_test_listing(test_client):
    response = test_client.get(listings_endpoint)
    assert response.status_code == 200
    returned_content = response.text  #.decode('utf-8')
    assert "lindo objeto a venda" in returned_content
    # invoke a specific link
    print(f"to call now: {listings_endpoint}/Apto101/0")
    response = test_client.get(f"{single_listing_endpoint}/Apto101/0")
    assert response.status_code == 200
    returned_content = response.text  #.decode('utf-8')
    assert "lindo objeto a venda" in returned_content
    assert "Posted" in returned_content
    assert "Preço" in returned_content

def exec_test_login(test_client):
    response = test_client.get(login_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Logar" in returned_content
    assert "Usuário" in returned_content
    assert "Senha" in returned_content

def exec_test_login_redirect(test_client):
    response = test_client.get(login_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Início" in returned_content
    assert "Condominio do Edificio Rivera" in returned_content
    assert "Bem-vindo" in returned_content

def exec_test_logged_in_menu(test_client):
    response = test_client.get(login_endpoint)
    assert response.status_code == 200
    returned_content = response.text
    assert "Início" in returned_content
    assert "Cadastrar" in returned_content
    assert "Modificar" in returned_content
    assert "Reservas" in returned_content
    assert "Multas & Cobranças" in returned_content
    assert "Anúncios" in returned_content
    assert "Documentos" in returned_content
    assert "Manutenção" in returned_content
    assert "Fotos" in returned_content
    assert "À Venda" in returned_content
    assert "Sobre" in returned_content
    assert "Logout" in returned_content



def login(test_client, tenant, username, password):
    data = {'userid': username, 'password': password}
    response = test_client.post(f"http://localhost:5000/{tenant}/login", data=data, follow_redirects=True)
    assert response.status_code == 200
    return response.status_code
