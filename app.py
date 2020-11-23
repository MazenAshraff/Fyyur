#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import copy
import dateutil.parser
import babel
import sys
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Artist,Venue,Shows,app,db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app.config.from_object('config')
moment = Moment(app)
migrate=Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
    # TODO: implement any missing fields, as a database migration using Flask-Migrate



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data=[]
  query = db.session.query(Venue.city.distinct().label("city"))
  cities = [row.city for row in query.all()]
  query = db.session.query(Venue.state.distinct().label("state"))
  states = [row.state for row in query.all()]
  for city in cities:
    entry1 = {"city":city}
    for state in states:
      entry2 = copy.deepcopy(entry1)
      entry2["state"]=state

      query =  db.session.query(Venue).outerjoin(Shows).filter(Venue.city==city,Venue.state==state)
      thevenues=query.all()
      venues=[]
      for q in thevenues:
        venue ={"id":q.id,
        "name":q.name,
        "num_upcoming_shows":len(Shows.query.filter(Shows.venueId==q.id,Shows.datetime>datetime.now()).all())}
        venues.append(venue)

    
      entry2["venues"]=venues
      if len(entry2["venues"])>0:  
        data.append(entry2)
  print(data) 
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = request.form.get('search_term','')
  
  venues = Venue.query.filter(Venue.name.ilike(f'%{data}%'))
  count = venues.count()
  venues = venues.all()
  responseData = []
  for venue in venues:
    v={"id":venue.id,"name":venue.name,"num_upcoming_shows":Shows.query.filter(Shows.venueId==venue.id,Shows.datetime>datetime.now()).count()}
    responseData.append(v)
  response={
    "count": count,
    "data": responseData
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = db.session.query(Shows).join(Venue).filter(Shows.venueId == Venue.id,
  Shows.datetime < datetime.now(),
  Venue.id==venue_id
  ).all()
  upcoming_shows=db.session.query(Shows).join(Venue).filter(
  Shows.venueId == Venue.id,
  Shows.datetime > datetime.now(),
  Venue.id==venue_id
  ).all()
  print(upcoming_shows)
  venue = Venue.query.filter(Venue.id==venue_id).first()
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    talent_seek=False
    if request.form.get('seeking_talent')=='y':
          talent_seek=True
    v = Venue(
      name=request.form.get('name'),
      city= request.form.get('city'),
      state = request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      website=request.form.get('website'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      seeking_talent=talent_seek,
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(v)
    db.session.commit()
    print('Commited successsfully')
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()    
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    ven = Venue.query.filter(Venue.id==venue_id)
    db.session.delete(ven)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()    
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.with_entities(Artist.name,Artist.id)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = request.form.get('search_term','')
  
  artists = Artist.query.filter(Artist.name.ilike(f'%{data}%'))
  count = artists.count()
  artists = artists.all()
  responseData = []
  for artist in artists:
    a={"id":artist.id,"name":artist.name,"num_upcoming_shows":Shows.query.filter(Shows.artistId==artist.id,Shows.datetime>datetime.now()).count()}
    responseData.append(a)
  response={
    "count": count,
    "data": responseData
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows = db.session.query(Shows).join(Artist).filter(
  Shows.artistId == Artist.id,
  Shows.datetime < datetime.now(),
  Artist.id==artist_id
  )
  upcoming_shows=db.session.query(Shows).join(Artist).filter(
  Shows.artistId == Artist.id,
  Shows.datetime > datetime.now(),
  Artist.id==artist_id
  )
  artist = Artist.query.filter(Artist.id==artist_id).first()
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows_count": past_shows.count(),
    "upcoming_shows_count": upcoming_shows.count(),
    "past_shows": past_shows.all(),
    "upcoming_shows": upcoming_shows.all()

  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist =Artist.query.filter(Artist.id==artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    venue_seek = False
    if request.form.get('seeking_venue')=='y':
          venue_seek=True
    artist= Artist.query.filter(Artist.id==artist_id).first()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.address = request.form.get('address')
    artist.phone = request.form.get('phone')
    artist.website = request.form.get('website')
    artist.genres = request.form.get('genres')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_description = request.form.get('seeking_description')
    artist.seeking_venue = venue_seek
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue =Venue.query.filter(Venue.id==venue_id)[0]
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    talent_seek = False
    if request.form.get('seeking_talent')=='y':
          talent_seek=True
    venue= Venue.query.filter(Venue.id==venue_id).first()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.website = request.form.get('website')
    venue.genres = request.form.get('genres')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.seeking_description = request.form.get('seeking_description')
    venue.seeking_talent = talent_seek
    db.session.commit()
  except Exception as e:
    db.session.rollback()
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
  print(request.form.get('genres'),request.form.get('facebook_link'))
  try:
    venue_seek=False
    if(request.form.get('seeking_venue')=='y'):
          venue_seek=True
    
    artist = Artist(
      name=request.form.get('name'),
      city= request.form.get('city'),
      state = request.form.get('state'),
      phone=request.form.get('phone'),
      genres=request.form.get('genres'),
      website=request.form.get('website'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      seeking_venue=venue_seek,
      seeking_description=request.form.get('seeking_description')
    )
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = Shows.query.all()

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    s = Shows(datetime=request.form.get('start_time'),artistId=request.form.get('artist_id'),venueId=request.form.get('venue_id'))
    db.session.add(s)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()    
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
