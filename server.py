import json
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    with open('clubs.json') as c:
        list_of_clubs = json.load(c)['clubs']
        return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        return list_of_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()


@app.route('/')
def index():
    return render_template('index.html')


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


@app.route('/showSummary',methods=['POST'])
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
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions if c['name'] == competition][0]
    if found_club and found_competition:
        return render_template('booking.html', club=found_club, competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


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
        competition['numberOfPlaces'] = nbr_places - places_required
        return True
    else:
        return False


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]

    places_required = int(request.form['places'])

    if update_places(competition, places_required, club):
        flash('Great-booking complete!')
    else:
        flash('You tried to book an invalid number of places, sorry')

    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))