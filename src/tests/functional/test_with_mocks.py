"""
  To run these tests:
  . cd to the root folder "condospace"
  . pytest src/tests/functional/test_with_mocks.py
"""

from importmonkey import add_path
add_path("/home/joe/Documents/test-servers/condospace/src")  # relative to current __file__


#from server import create_app  # Replace my_app with your application's import
from aws import AWS
from users import UsersRepository
import pytest
from typing import Dict, Any
import requests
import os
import pytest
from moto import mock_aws
import boto3
from moto import mock_aws
import json


# production code
def calculate_discount(price, discount_provider):
    percentage = discount_provider.get_percentage()
    return price - (price * percentage / 100)

# production code
def get_weather(city: str) -> Dict:
    """
    Function to get weather
    :return: Response from the API
    """
    response = requests.get(f"https://goweather.herokuapp.com/weather/{city}")
    return response.json()

# production code
def process_payment(payment_gateway, amount):
    response = payment_gateway.charge(amount)
    if response == "Success":
        return "Payment processed successfully"
    else:
        raise ValueError("Payment failed")

# production class
class Person:
    def __init__(self, name: str, age: int = None, address: str = None) -> None:
        self._name = name
        self._age = age
        self._address = address

    @property
    def name(self) -> str:
        return self._name

    @property
    def age(self) -> int:
        return self._age

    @property
    def address(self) -> str:
        return self._address

    def get_person_json(self) -> Dict[str, str]:
        return {"name": self._name, "age": self._age, "address": self._address}

    def get_majority_declaration(self):
        decl = "an adult" if self.age >= 17 else "a minor"
        return f"{self._name} is {decl}"


# production code
def get_aws_object(bucket: str, key: str) -> Any:
    """
    Function to get an object from S3
    :param bucket: Bucket name
    :param key: Key name
    :return: Response from S3
    """
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response


#-----------------------------------------------------------------------------------------
#  test code
#-----------------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@pytest.fixture(scope="function")
def aws_s3(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")

def test_person_class_with_mock(mocker):
    """
    Test the Person class using a mock for the 'get_person_json' method
    """
    person = Person(name="Eric", age=17, address="123 Farmville Rd")
    expected_response = "Eric is an adult"
    # Patch the method
    mocker.patch.object(person, "get_majority_declaration", return_value=expected_response)
    assert person.get_majority_declaration() == expected_response

# test our production code by passing a mock object
def test_calculate_discount(mocker):
    # Mock the get_percentage method
    mock_discount_provider = mocker.Mock()
    mock_discount_provider.get_percentage.return_value = 10  # Mocked discount value
    # Call the function with the mocked dependency
    result = calculate_discount(100, mock_discount_provider)
    # Assert the calculated discount is correct
    assert result == 90
    mock_discount_provider.get_percentage.assert_called_once()

# test code
def test_process_payment_with_side_effects(mocker):
    # Mock the charge method of the payment gateway
    mock_payment_gateway = mocker.Mock()
    # Add side effects: Success on first call, raise exception on second call
    mock_payment_gateway.charge.side_effect = ["Success", ValueError("Insufficient funds")]
    # Test successful payment
    assert process_payment(mock_payment_gateway, 100) == "Payment processed successfully"
    # Test payment failure
    with pytest.raises(ValueError, match="Insufficient funds"):
        process_payment(mock_payment_gateway, 200)
    # Verify the mock's behavior
    assert mock_payment_gateway.charge.call_count == 2

def test_get_weather_mocked(mocker):
    mock_data = {
        "temperature": "+7 °C",
        "wind": "13 km/h",
        "description": "Partly cloudy",
        "forecast": [
            {"day": "1", "temperature": "+10 °C", "wind": "13 km/h"},
            {"day": "2", "temperature": "+6 °C", "wind": "26 km/h"},
            {"day": "3", "temperature": "+15 °C", "wind": "21 km/h"},
        ],
    }

    # Create a mock response object with a .json() method that returns the mock data
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = mock_data

    # Patch 'requests.get' to return the mock response
    mocker.patch("requests.get", return_value=mock_response)

    # Call the function
    result = get_weather(city="London")

    # Assertions to check if the returned data is as expected
    assert result == mock_data
    assert type(result) is dict
    assert result["temperature"] == "+7 °C"
    assert result['forecast'][0]['temperature'] == "+10 °C"

@mock_aws
def test_get_my_object_mocked(aws_s3):
    """
    Function to test get my object
    :param s3: pytest-mock fixture
    :return: None
    """
    # Create a mock S3 bucket.
    json_obj = {'userid': 'joe', 'name': 'joe silva', 'email': 'joe@gmail.com'}
    aws_s3.create_bucket(Bucket="mock-bucket")
    # Create a mock object in the mock S3 bucket.
    aws_s3.put_object(Bucket="mock-bucket", Key="mock-key", Body=json.dumps(json_obj))
    # Get the mock object from the mock S3 bucket.
    response = get_aws_object(bucket="mock-bucket", key="mock-key")
    json_back = json.loads(response["Body"].read())
    assert json_back['userid'] == 'joe'
    assert json_back['name'] == 'joe silva'
    assert json_back['email'] == 'joe@gmail.com'



