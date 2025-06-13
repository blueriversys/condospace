
import requests
import time

def invoke_with_context():
    login_data = {
        "userid": "super_adm",
        "password": "edificioalfa@1745321775"
    }
    with requests.Session() as client:
        login_response = client.post('http://localhost:5000/edificioalfa/login', data=login_data)
        if login_response.status_code == 302: # Check for redirect
            print(f"this should never happens")
            exit(0)

        # we need to invoke the secure endpoint
        print(f"status_code here: {login_response.status_code} ")
        for i in range(5):
            success = invoke_secure_ep(client)
            if not success:
                print(f"unexpected execution of invoke_secure_ep(): status {success}")
                exit(0)
            time.sleep(3)

        # now invoke the unsecure endpoint
        for i in range(5):
            response = client.get("http://localhost:5000/edificioalfa/login_not_required")
            if response.status_code != 200:
                print(f"unexpected execution of invoke_secure_ep(): status {success}")
                exit(0)
            else:
                print("invoke UNSECURE is success")
            time.sleep(3)

        # now invoke logout
        logout_response = client.get('http://localhost:5000/edificioalfa/logout')
        print(f"logout response: {logout_response.status_code}")


def invoke_secure_ep(client):
    payload_check_id = {
        "condo_id": 'edificioalfa',
        "field1": '',
        "field2": ''
    }
    response = client.get("http://localhost:5000/edificioalfa/login_required", json=payload_check_id)
    if response.status_code == 200:
        if response.json()['status'] == 'error':
            print("client: error invoking the secure ep")
            return False
        else:
            print(f"client: invokation success")
            return True
    return False


def main():
    invoke_with_context()

if __name__ == "__main__":
    main()
