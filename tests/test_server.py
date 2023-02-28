from server import create_app
import pytest

"""
TODO:
- Get Board in a function
- Get Board calling the previous function
- Log in (subfunction)
- Log in (test)
- Log in (wrong mail)
- Log out (test)
- 
"""


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


def test_get_login_page(client):
    rv = client.get("/", follow_redirects=True)
    assert rv.status_code == 200
    data = rv.data.decode()
    assert data.find("Welcome to the GUDLFT Registration Portal!") != -1


def test_login_fail(client):
    rv = client.post(
        "/showSummary", data=dict(email="john@simplylift.com"), follow_redirects=True
    )
    # assert rv.status_code == 200
    data = rv.data.decode()
    assert data.find("Sorry, that email") > -1


def test_login_successful(client):
    rv = client.post(
        "/showSummary", data=dict(email="john@simplylift.com"), follow_redirects=True
    )
    # assert rv.status_code == 200
    data = rv.data.decode()
    assert data.find("Sorry, that email") > -1