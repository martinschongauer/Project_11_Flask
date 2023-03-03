from server import check_email, load_competitions, load_clubs, update_places, check_date_validity
import pytest


@pytest.fixture
def database_fixture():
    data = {"competition_1": load_competitions()[0],
            "competition_2": load_competitions()[1],
            "club_1": load_clubs()[0],
            "club_2": load_clubs()[1]}
    return data


def test_invalid_email():
    invalid_mail = 'invalid@simplylift.co'
    club = check_email(invalid_mail)
    assert not club


def test_valid_email():
    valid_mail = 'john@simplylift.co'
    club = check_email(valid_mail)
    assert club['email'] == valid_mail


def test_more_than_12_places(database_fixture):
    places_required = 13
    return_value = update_places(database_fixture['competition_1'], places_required, database_fixture['club_1'])
    assert not return_value


def test_less_than_1_place(database_fixture):
    places_required = 0
    return_value = update_places(database_fixture['competition_1'], places_required, database_fixture['club_1'])
    assert not return_value


def test_10_places(database_fixture):
    places_required = 10
    return_value = update_places(database_fixture['competition_1'], places_required, database_fixture['club_1'])
    assert return_value


def test_not_enough_points(database_fixture):
    places_required = 10
    return_value = update_places(database_fixture['competition_1'], places_required, database_fixture['club_2'])
    assert not return_value


def test_club_points_updated(database_fixture):
    club = database_fixture['club_1']
    places_required = 10
    expected_points = int(club['points']) - places_required
    update_places(database_fixture['competition_1'], places_required, club)
    assert int(club['points']) == expected_points


def test_invalid_date(database_fixture):
    competition = database_fixture['competition_2']
    assert not check_date_validity(competition)


def test_valid_date(database_fixture):
    competition = database_fixture['competition_1']
    assert check_date_validity(competition)
