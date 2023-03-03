from server import create_app
import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as client:
        yield client


"""
    TESTS FOR LOGINS AND LOGOUT
"""


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
    login_mail = "john@simplylift.co"
    rv = client.post(
        "/showSummary", data=dict(email=login_mail), follow_redirects=True
    )
    assert rv.status_code == 200
    data = rv.data.decode()
    assert data.find(f"Welcome, {login_mail}") > -1


def test_logout(client):
    login_mail = "john@simplylift.co"
    rv = client.post(
        "/showSummary", data=dict(email=login_mail), follow_redirects=True
    )
    assert rv.status_code == 200
    data = rv.data.decode()

    # Get all links in the page - first one should be the logout
    soup = BeautifulSoup(data, 'html.parser')
    links = soup.find_all("a")
    href = links[0].get("href")

    # And try the logout
    rv = client.get(href, follow_redirects=True)
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("Welcome to the GUDLFT Registration Portal!") != -1


"""
    TESTING THE POINTS BOARD
"""


def test_get_points_board(client):
    rv = client.get("/printClubs", follow_redirects=True)
    assert rv.status_code == 200
    data = rv.data.decode()

    # Find <td> tags, they contain mails and points
    soup = BeautifulSoup(data, 'html.parser')
    cells = soup.find_all("td")

    email = "john@simplylift.co"
    john_points = 13
    points = 0
    next_cell = False

    # Looking for a cell that contains a given email, and extract the content of the next one
    for cell in cells:
        if cell.contents[0] == email:
            next_cell = True
            continue
        if next_cell:
            points = int(cell.contents[0])
            break

    assert points == john_points


"""
    TESTING BOOKING
"""


def test_spring_festival(client):
    login_mail = "john@simplylift.co"
    rv = client.post(
        "/showSummary", data=dict(email=login_mail), follow_redirects=True
    )
    assert rv.status_code == 200
    data = rv.data.decode()

    # Get all links in the page - second one should allow to book for the spring festival
    soup = BeautifulSoup(data, 'html.parser')
    links = soup.find_all("a")
    href = links[1].get("href")

    # Enter the booking page...
    rv = client.get(href, follow_redirects=True)
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("Places available: 25") != -1


def test_fall_classic_fail(client):
    login_mail = "john@simplylift.co"
    rv = client.post(
        "/showSummary", data=dict(email=login_mail), follow_redirects=True
    )
    assert rv.status_code == 200
    data = rv.data.decode()

    # Get all links in the page - third one should point to an outdated competition
    soup = BeautifulSoup(data, 'html.parser')
    links = soup.find_all("a")
    href = links[2].get("href")

    # We should be rejected
    rv = client.get(href, follow_redirects=True)
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("Selected competition is over") != -1


def test_invalid_booking(client):
    club = "Simply Lift"
    competition = "Spring Festival"
    places = "20"

    # Book an excessive amount of places
    rv = client.post(
        "/purchasePlaces",
        data=dict(club=club, competition=competition, places=places),
        follow_redirects=True
        )
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("You tried to book an invalid number of places") != -1


def test_invalid_booking_2(client):
    club = "Simply Lift"
    competition = "Spring Festival 2"
    places = "11"

    # This time, we should be rejected because there are not enough places left for the competition
    rv = client.post(
        "/purchasePlaces",
        data=dict(club=club, competition=competition, places=places),
        follow_redirects=True
        )
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("You tried to book an invalid number of places") != -1


def test_invalid_club_name(client):
    club = "Invalid"
    competition = "Spring Festival"
    places = "10"

    # Purchase with a non-existing club name
    rv = client.post(
        "/purchasePlaces",
        data=dict(club=club, competition=competition, places=places),
        follow_redirects=True
        )
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("Welcome to the GUDLFT Registration Portal!") != -1


def test_invalid_competition_name(client):
    url = "/book/Invalid/Simply%20Lift"

    # Getting an invalid booking URL
    rv = client.get(url,follow_redirects=True)
    assert rv.status_code == 200

    data = rv.data.decode()
    assert data.find("Welcome to the GUDLFT Registration Portal!") != -1


def test_valid_booking(client):
    club = "Simply Lift"
    competition = "Spring Festival"
    places = "10"
    points_available = 3

    # Book 10 places -> redirected to main page
    rv = client.post(
        "/purchasePlaces",
        data=dict(club=club, competition=competition, places=places),
        follow_redirects=True
        )
    assert rv.status_code == 200

    # Check that the points were updated
    data = rv.data.decode()
    assert data.find(f"Points available: {points_available}") != -1

    # Check that the points were also updated on the board
    rv = client.get("/printClubs", follow_redirects=True)
    assert rv.status_code == 200
    data = rv.data.decode()
    soup = BeautifulSoup(data, 'html.parser')
    cells = soup.find_all("td")

    email = "john@simplylift.co"
    points = 0
    next_cell = False

    # Looking for a cell that contains a given email, and extract the content of the next one
    for cell in cells:
        if cell.contents[0] == email:
            next_cell = True
            continue
        if next_cell:
            points = int(cell.contents[0])
            break

    assert points == points_available
