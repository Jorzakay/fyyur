#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import (ArtistAvailability, Show, Artist, Venue, db)
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import func
from sqlalchemy import or_, and_
from errors import ArtistBooked
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    db.init_app(app)
    return app
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    recent_artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    recent_venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    cities = db.session.query(Venue.city, Venue.state,
                              ).distinct().all()

    data = []
    for (city, state) in cities:
        venues = Venue.query.with_entities(
            Venue.id, Venue.name, Venue.num_upcoming_shows).filter_by(city=city, state=state).all()

        d = {"city": city, "state": state,
             "venues": venues}

        data.append(d)

    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term")
    venues = Venue.query.with_entities(
        Venue.id,
        Venue.name,
        Venue.num_upcoming_shows
    ).filter(
        or_(
            Venue.name.ilike(f"%{search_term}%"),
            Venue.city_state.ilike(search_term)
        )
    )
    count = venues.count()
    response = {
        "count": count,
        "data": venues
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id

    venue = Venue.query.get(venue_id)
    shows = venue.shows
    current_time = datetime.now()
    upcoming_shows = []
    past_shows = []
    for show in shows:
        show_obj = {
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > current_time:
            upcoming_shows.append(show_obj)
        else:
            past_shows.append(show_obj)

    venue.upcoming_shows = upcoming_shows
    venue.past_shows = past_shows
    venue.past_shows_count = len(past_shows)
    venue.upcoming_shows_count = len(upcoming_shows)
    venue.genres = venue.genres.split(",")
    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form_data = VenueForm()
    genres = ",".join(form_data.getlist("genres"))
    new_venue = Venue(
        name=form_data.name.data,
        city=form_data.city.data,
        state=form_data.state.data,
        address=form_data.address.data,
        phone=form_data.phone.data,
        image_link=form_data.image_link.data,
        facebook_link=form_data.facebook_link.data,
        genres=genres,
        website=form_data.website_link.data,
        seeking_talent=form_data.seeking_talent.data,
        seeking_description=form_data.seeking_description.data,
    )
    try:
        db.session.add(new_venue)
    except Exception as e:
        db.rollback()
        flash("An error occurred. Venue " +
              form_data.name.data + " could not be listed.")
    else:
        db.session.commit()
        flash('Venue ' + new_venue.name + ' was successfully listed!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id)
    try:
        venue.delete()
    except:
        db.session.rollback()
        db.session.close()
        return "This venue coould not be deleted.", 400
    else:
        db.session.commit()
        db.session.close()
    return "success"

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    artists = Artist.query.with_entities(Artist.id, Artist.name)
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term")
    artists = Artist.query.filter(
        or_(
            Artist.name.ilike(f"%{search_term}%"),
            Artist.city_state.ilike(search_term)
        )
    )
    data = []
    for artist in artists:

        num_upcoming_shows = Show.query.filter(
            Show.artist_id == artist.id, Show.start_time > datetime.now()).count()
        artist_data = {"id": artist.id, "name": artist.name,
                       "num_upcoming_shows": num_upcoming_shows}
        data.append(artist_data)

    response = {
        "count": artists.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id

    artist = Artist.query.get(artist_id)
    shows = artist.shows
    current_time = datetime.now()
    upcoming_shows = []
    past_shows = []
    for show in shows:
        show_obj = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": str(show.start_time)
        }
        if show.start_time > current_time:
            upcoming_shows.append(show_obj)
        else:
            past_shows.append(show_obj)

    artist.upcoming_shows = upcoming_shows
    artist.past_shows = past_shows
    artist.past_shows_count = len(past_shows)
    artist.upcoming_shows_count = len(upcoming_shows)
    artist.genres = artist.genres.split(",")

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = Artist.query.get(artist_id)
    artist.genres = artist.genres.split(",")
    form = ArtistForm(obj=artist)
    form.website_link.data = artist.website
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form_data = ArtistForm()
    try:
        genres = ",".join(form_data.genres.data)
        artist = Artist.query.get(artist_id)
        artist.name = form_data.name.data
        artist.city = form_data.city.data
        artist.state = form_data.state.data
        artist.phone = form_data.phone.data
        artist.image_link = form_data.image_link.data
        artist.facebook_link = form_data.facebook_link.data
        artist.genres = genres
        artist.website = form_data.website_link.data
        artist.seeking_venue = form_data.seeking_venue.data
        artist.seeking_description = form_data.seeking_description.data

        # for availability in form_data.availabilities.data:
        current_availabilities = []
        new_availabilities = []

        for d in form_data.availabilities.data:
            _id = d.get("id")
            if _id:
                current_availabilities.append(d)
            else:
                if d.get('day') and d.get('time_from') and d.get('time_to'):
                    new_availabilities.append(ArtistAvailability(
                        artist_id=artist.id,
                        time_from=d.get('time_from'),
                        day=d.get('day'),
                        time_to=d.get('time_to')
                    ))
        for availability in current_availabilities:
            _id = availability.get("id")
            day = availability.get('day')
            time_from = availability.get('time_from')
            time_to = availability.get('time_to')
            if _id and day and time_from and time_to:
                a = ArtistAvailability.query.get(_id)
                a.day = day
                a.time_from = time_from
                a.time_to = time_to
            else:
                a = ArtistAvailability.query.filter_by(
                    id=_id)
                a.delete()

        if len(new_availabilities) > 0:
            db.session.add_all(new_availabilities)

    except Exception as e:
        db.session.rollback()
        flash(f"Could not update artist. {str(e)}")
    else:

        db.session.commit()
        flash(f"{ artist.name } has been updated.")
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.website_link.data = venue.website
    form.genres.data = venue.genres.split(",")
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form_data = VenueForm()
    try:
        genres = ",".join(form_data.genres.data)
        venue.name = form_data.name.data
        venue.city = form_data.city.data
        venue.state = form_data.state.data
        venue.phone = form_data.phone.data
        venue.image_link = form_data.image_link.data
        venue.facebook_link = form_data.facebook_link.data
        venue.genres = genres
        venue.website = form_data.website_link.data
        venue.seeking_talent = form_data.seeking_talent.data
        venue.seeking_description = form_data.seeking_description.data
        venue.address = form_data.address.data
    except Exception as e:
        db.session.rollback()
        flash(f"Could not update venue. Error: {str(e)}")
    else:
        db.session.commit()
        flash(f"{ venue.name } has been updated.")

    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form_data = ArtistForm()

    genres = ",".join(form_data.genres.data)
    new_artist = Artist(
        name=form_data.name.data,
        city=form_data.city.data,
        state=form_data.state.data,
        phone=form_data.phone.data,
        image_link=form_data.image_link.data,
        facebook_link=form_data.facebook_link.data,
        genres=genres,
        website=form_data.website_link.data,
        seeking_venue=form_data.seeking_venue.data,
        seeking_description=form_data.seeking_description.data,

    )

    try:
        db.session.add(new_artist)
        db.session.flush()
        availabilities = [ArtistAvailability(
            artist_id=new_artist.id,
            time_from=d.get('time_from'),
            day=d.get('day'),
            time_to=d.get('time_to')
        ) for d in form_data.availabilities.data if d.get('day') and d.get('time_from') and d.get('time_to')]

        db.session.add_all(availabilities)
    except Exception as e:
        db.rollback()
        flash("An error occurred. Artist " +
              form_data.name.data + " could not be listed.")
    else:
        db.session.commit()
        flash('Artist ' + new_artist.name + ' was successfully listed!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    shows = Show.query.with_entities(
        Show.venue_id.label("venue_id"),
        Venue.name.label("venue_name"),
        Show.artist_id.label("artist_id"),
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        func.to_char(Show.start_time,
                     'YYYY-MM-DD HH24:MI:SS').label("start_time")
    ).join(Venue).join(Artist).all()

    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm()
    show = Show(
        venue_id=form.venue_id.data,
        artist_id=form.artist_id.data,
        start_time=form.start_time.data
    )

    start_time = show.start_time

    start_time_day = start_time.isoweekday()
    start_time_time = start_time.time()

    is_available = ArtistAvailability.query.filter(ArtistAvailability.day == start_time_day, and_(
        ArtistAvailability.time_from <= start_time_time,
        ArtistAvailability.time_to >= start_time_time,
    )).count() > 0

    try:
        if is_available:
            db.session.add(show)
        else:

            raise ArtistBooked("This artist is not available at this time")
    except ArtistBooked as e:
        flash(str(e))
    except Exception:
        flash('An error occurred. Show could not be listed.')
        db.session.rollback()
    else:
        db.session.commit()
        flash('Show was successfully listed!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=app.config.get("DEBUG", False))

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
