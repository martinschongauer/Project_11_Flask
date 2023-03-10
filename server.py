import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


def check_email(email: str) -> dict:
    """Finds, if it exists, the club associated with a given secretary email

    param email : email used as an ID for a club secretary
    return : club infos for this email - empty if email is unknown
    """
    clubs_found = []
    for club in clubs:
        if club['email'] and club['email'] == email:
            clubs_found.append(club)

    if not clubs_found:
        return {}
    else:
        return clubs_found[0]


def check_date_validity(competition: dict) -> bool:
    """Checks whether a given competition is over through its date

    param competition: dictionary containing competition infos
    return: True if we can subscribe to a competition (future competition)
    """
    current_time = datetime.now()
    competition_time_str = competition['date']
    competition_time = datetime.strptime(competition_time_str, "%Y-%m-%d %H:%M:%S")
    return current_time < competition_time


def update_places(competition: dict, places_required: int, club: dict) -> bool:
    """Book (and deduce) places in a given competition

    param competition: dictionary loaded from database and describing a competition
    param places_required: how many places the club wants to book
    return: True if the places could be booked
    """
    nbr_places = int(competition['numberOfPlaces'])
    club_nbr_points = int(club['points'])

    # Pay attention to the 12 places limit for each club, and the number of points available
    if (0 < places_required < 13) and (places_required <= club_nbr_points):
        competition_places = nbr_places - places_required
        # Make sure that the competition cannot run out of places
        if competition_places < 0:
            return False
        # Update values in both competition and club dictionaries
        competition['numberOfPlaces'] = competition_places
        club_nbr_points = club_nbr_points - places_required
        club['points'] = str(club_nbr_points)
        return True
    else:
        return False


competitions = load_competitions()
clubs = load_clubs()


def get_club_and_competition(club: str, competition: str) -> (bool, dict, dict):
    """Retrieve a club and a competition in the list, with their name

    param club: club name
    param competition: competition name
    return: True if they were found + objects
    """
    competition = [c for c in competitions if c['name'] == competition]
    club = [c for c in clubs if c['name'] == club]

    # Something wrong
    if not competition or not club:
        return False, None, None

    # No error
    return True, club[0], competition[0]


def create_app():
    app = Flask(__name__)
    # app.config.from_object(config)
    app.secret_key = 'something_special'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary', methods=['POST'])
    def show_summary():
        """Log in and render main page
        """
        club = check_email(request.form['email'])

        # Detect invalid (=unknown) email -> redirect to index page
        if not club:
            return render_template('index.html', email_error=True)
        else:
            return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/book/<competition>/<club>')
    def book(competition, club):
        ok_flag, found_club, found_competition = get_club_and_competition(club, competition)

        # Invalid URL, should not happen (hack attempt? -> Kick user back to login page)
        if not ok_flag:
            return redirect("/")

        # Make sure that the competition does not belong to the past...
        if not check_date_validity(found_competition):
            flash("Selected competition is over")
            return render_template('welcome.html', club=found_club, competitions=competitions)

        # If we arrived here, it's OK
        max_places = min(12, int(found_club['points']), int(found_competition['numberOfPlaces']))
        return render_template('booking.html',
                               club=found_club,
                               competition=found_competition,
                               max_places=max_places)

    @app.route('/purchasePlaces', methods=['POST'])
    def purchase_places():
        ok_flag, club, competition = get_club_and_competition(request.form['club'], request.form['competition'])

        # Most probably some malicious attempt...
        if not ok_flag:
            return redirect("/")

        places_required = int(request.form['places'])

        if update_places(competition, places_required, club):
            flash('Great-booking complete!')
        else:
            flash('You tried to book an invalid number of places, sorry')

        return render_template('welcome.html', club=club, competitions=competitions)

    @app.route('/printClubs')
    def print_clubs():
        return render_template('board.html', clubs=clubs)

    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app
