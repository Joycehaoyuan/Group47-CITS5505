import json
from bs4 import BeautifulSoup

def test_register_and_login(client):
    # Register
    rv = client.post(
        '/register',
        data={
            'username': 'user1',
            'email': 'u1@example.com',
            'password': 'Passw0rd!',
            'password_confirm': 'Passw0rd!'
        },
        follow_redirects=True
    )
    assert b'Your account has been created' in rv.data

    # Login
    rv = client.post(
        '/login',
        data={
            'username': 'user1',
            'password': 'Passw0rd!'
        },
        follow_redirects=True
    )
    assert b'Login successful' in rv.data
