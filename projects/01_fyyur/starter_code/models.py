from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from sqlalchemy import select, func
from sqlalchemy.sql import case

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship(
        "Show", backref="venue", lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Venue: id: {self.id} name: {self.name} />"

    @hybrid_property
    def city_state(self):
        if self.city is not None:
            return self.city + ", " + self.state
        else:
            return self.state

    @city_state.expression
    def city_state(cls):
        return case([
            (cls.city != None, cls.city + ", " + cls.state),
        ], else_=cls.state)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref="artist",
                            lazy=True, cascade="all, delete-orphan")

    availabilities = db.relationship('ArtistAvailability', backref="artist",
                                     lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Artist: id: {self.id} name: {self.name} />"

    @hybrid_property
    def city_state(self):
        if self.city is not None:
            return self.city + ", " + self.state
        else:
            return self.state

    @city_state.expression
    def city_state(cls):
        return case([
            (cls.city != None, cls.city + ", " + cls.state),
        ], else_=cls.state)


class ArtistAvailability(db.Model):
    __tablename__ = "ArtistAvailability"
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "Artist.id"), nullable=False)
    day = db.Column(db.Integer, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)

    @property
    def day_name(self):
        if self.day == 1:
            return "Monday"
        if self.day == 2:
            return "Tuesday"
        if self.day == 3:
            return "Wednesday"
        if self.day == 4:
            return "Thursday"
        if self.day == 5:
            return "Friday"
        if self.day == 6:
            return "Saturday"
        if self.day == 7:
            return "Sunday"
        return None


class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        "Artist.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


Venue.num_upcoming_shows = column_property(
    select(func.count(Show.id)).
    where(Show.venue_id == Venue.id).
    scalar_subquery()
)
