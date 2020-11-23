from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website=db.Column(db.String(120))
    genres=db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String(500),default="Not Currently Seeking talent")
    def __repr__(self):
          return f'{self.name} {self.city} {self.state} {self.address} {self.phone} {self.website} {self.genres} {self.image_link} {self.facebook_link} {self.seeking_talent} {self.seeking_description}'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500),default='Not looking for venues')

class Shows(db.Model):
      __tablename__='Shows'
      id =db.Column(db.Integer,primary_key=True)
      datetime = db.Column(db.DateTime,nullable=False)
      artistId= db.Column(db.Integer,db.ForeignKey('Artist.id'))
      venueId = db.Column(db.Integer,db.ForeignKey('Venue.id'))


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

