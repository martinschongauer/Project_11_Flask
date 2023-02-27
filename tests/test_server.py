from server import check_email, load_competitions, load_clubs, update_places


def test_invalid_email():
    invalid_mail = 'invalid@simplylift.co'
    club = check_email(invalid_mail)
    assert not club


def test_valid_email():
    valid_mail = 'john@simplylift.co'
    club = check_email(valid_mail)
    assert club['email'] == valid_mail


def test_more_than_12_places():
    competitions = load_competitions()
    competition = competitions[0]
    clubs = load_clubs()
    club = clubs[0]

    places_required = 13
    return_value = update_places(competition, places_required, club)
    assert not return_value


def test_less_than_1_place():
    competitions = load_competitions()
    competition = competitions[0]
    clubs = load_clubs()
    club = clubs[0]

    places_required = 0
    return_value = update_places(competition, places_required, club)
    assert not return_value


def test_10_places():
    competitions = load_competitions()
    competition = competitions[0]
    clubs = load_clubs()
    club = clubs[0]

    places_required = 10
    return_value = update_places(competition, places_required, club)
    assert return_value


def test_not_enough_points():
    competitions = load_competitions()
    competition = competitions[0]
    clubs = load_clubs()
    club = clubs[1]

    places_required = 10
    return_value = update_places(competition, places_required, club)
    assert not return_value
