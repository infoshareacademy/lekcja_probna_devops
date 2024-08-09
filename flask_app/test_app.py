"""
This file contains unit_tests
"""

import requests
import pytest

@pytest.mark.parametrize("url, expected_status, expected_data", [
    ('http://flask-app:5000/api/data', 200, {"message": "Hello, from Flask!"}),
    # Add more test cases as needed
])
def test_get_data(url, expected_status, expected_data):
    """
    test_get_data function to return a response
    """

    timeout = 10
    response = requests.get(url, timeout=timeout)
    data = response.json()

    assert response.status_code == expected_status
    assert data == expected_data
