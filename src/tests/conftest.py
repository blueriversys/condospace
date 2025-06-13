import pytest
import requests
from importmonkey import add_path
add_path("/home/joe/Documents/test-servers/condospace/src")  # relative to current __file__


from server import create_app  # Replace my_app with your application's import
from models.users import SimpleUser
from flask_login import login_user
from functional.test_server import login_using_client

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def authenticated_user(app):
    print("in conftest.authenticated_user()")
    with app.test_request_context():
        user = SimpleUser(id=1, username="super_adm", password="edificioalfa@1745321775") # Create a test user
        login_user(user)
        yield user


@pytest.fixture(autouse=True)
def setup_and_teardown(app):
    """Fixture to execute code after each test."""
    print("in conftest.setup_and_teardown()")
    tenant = 'edificiorivera'
    user_id = 'AptoB101'
    login_data = {
        "userid": "super_adm",
        "password": "edificiorivera@1745321771"
    }

    with requests.Session() as test_client:
        if not login_using_client(test_client, tenant, login_data):
            raise Exception("setup_and_teardown(): login failure")
    print("\nFinished running setup code...")  # Code before yield is the "setup", code to run before each test

    yield test_client  # This is where the test function will run

    print("start of the teardown process...")
    logout_response = test_client.get(f'http://localhost:5000/{tenant}/logout')
    assert logout_response.status_code == 200
    print("Finished running teardown code.")  # Code after yield is the "teardown", code to run after each test


@pytest.fixture
def client(app):
    print("in conftest.client()")
    return app.test_client()
