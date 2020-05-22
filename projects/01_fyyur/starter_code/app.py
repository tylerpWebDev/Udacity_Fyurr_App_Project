#----------------------------------------------------------------------------# 
# Imports
#----------------------------------------------------------------------------#

import json
import ast
from datetime import datetime, timedelta
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.sql import func
import sys
import customFunctions as cfunc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------# 

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# =============================================================================
# =================  MY CUSTOM FUNCTOINS  =================
# =============================================================================


def cprint(string, label=""):
  print("\n\n")
  if len(label) > 0:
    print(label)
  print(string)
  print("\n\n")

def creating_single_show_objects(showData):
    genres_and_shows = []
    objectShowData = []
    finalGenres = []
    allVenueGenres = ""
    for x in showData:
      currentArtist = Artist.query.get(x.artist_id)
      

      if currentArtist.genres[len(currentArtist.genres)-1] != " ":
        currentArtist.genres = currentArtist.genres + ", "

      allVenueGenres = allVenueGenres + currentArtist.genres

      singleShow = {
              "id": x.id,
              "artist_id": x.artist_id, 
              "venue_id": x.venue_id,
              "artist_name":  currentArtist.name,
              "artist_image_link": currentArtist.image_link,
              "start_time": x.start_time
              }
      objectShowData.append(singleShow)

    allVenueGenres = allVenueGenres.strip()
    if len(allVenueGenres) > 0:
      if allVenueGenres[len(allVenueGenres)-1] == ",":
        allVenueGenres = allVenueGenres[0:len(allVenueGenres)-1]

    allVenueGenres = allVenueGenres.split(",")

    for x in allVenueGenres:
      if x.strip() not in finalGenres:
        finalGenres.append(x.strip())
    
    genres_and_shows.append(finalGenres)
    genres_and_shows.append(objectShowData)
    return genres_and_shows


def sortingPastShows(showData):
  upcomingShows = []
  pastShows = []
  currentDate = datetime.now()

  for s in showData:
    if currentDate > s["start_time"]:
      pastShows.append(s)
    else:
      upcomingShows.append(s)

  for x in upcomingShows:
    x["start_time"] = str(x["start_time"])
  for x in pastShows:
    x["start_time"] = str(x["start_time"])

  sorted_data = {
        "past_shows": pastShows,
        "upcoming_shows": upcomingShows,
        "past_shows_count": len(pastShows),
        "upcoming_shows_count": len(upcomingShows)
        }
  return sorted_data


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(1000), nullable=True)
    facebook_link = db.Column(db.String(500), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    seeking_talent = db.Column(db.Boolean(), default=True, nullable=True)
    shows = db.relationship('Show', backref='Venue', lazy=True)

    def __repr__(self):
        return '"id": {self.id}, "name": {self.name}, "city": {self.city}, "state": {self.state}, "address": {self.address}, "phone": {self.phone}, "image_link": {self.image_link}, "facebook_link": {self.facebook_link}'.format(self=self);



class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.String(120), nullable=True)
    image_link = db.Column(db.String(1000), nullable=True)
    facebook_link = db.Column(db.String(1000), nullable=True)
    shows = db.relationship('Show', backref='Artist', lazy=True)
    seeking_venue = db.Column(db.Boolean(), default=True, nullable=True)

    def __repr__(self):
        return '"id": {self.id}, "name": {self.name}, "city": {self.city}, "state": {self.state}, "phone": {self.phone}, "genres": {self.genres}, "image_link": {self.image_link}, "facebook_link": {self.facebook_link}, "seeking_venue": {self.seeking_venue}'.format(self=self);



class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime(), default=func.now(), nullable=True)

    def __repr__(self):
        return '"id": {self.id}, "artist_id": {self.artist_id}, "venue_id": {self.venue_id}, "start_time": {self.start_time}'.format(self=self);


db.create_all()

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

# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================

@app.route('/venues')
def venues():
  venueData = Venue.query.all()
  showData = Show.query.all()

  def countShows(venue_id, showData):
    count = 0
    for s in showData:
      if venue_id == s.venue_id:
        count = count + 1
    return count

  def formatVenueData(venueData):
    allCityStates = []
    for d in venueData:
      pair = {"city": d.city, "state": d.state}
      if pair not in allCityStates:
        allCityStates.append(pair)
    for a in allCityStates:
      a["venues"] = []

    for d in venueData:
      venuesObject = {"id": d.id, "name": d.name, "num_upcoming_shows": countShows(d.id, showData)}
      for a in allCityStates:
        if d.city == a["city"] and d.state == a["state"]:
          a["venues"].append(venuesObject)
    return allCityStates


  
  return render_template('pages/venues.html', areas=formatVenueData(venueData));
  


# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').lower()
  allVenues = Venue.query.all()
  allShows = Show.query.all()


  def filter_venues(search_term, allVenues):
    filtered_venues = []
    for x in allVenues:
      if search_term in x.name.lower():
        searchResult = {
                        "id": x.id,
                        "name": x.name,
                        "num_upcoming_shows": len(Show.query.filter(Show.venue_id == x.id, Show.start_time > datetime.now()).all()) 
                        }
        filtered_venues.append(searchResult)

    return filtered_venues

  filtered_venues = filter_venues(search_term, allVenues)

  response={
    "count": len(filtered_venues),
    "data": filtered_venues
  }

  if len(filtered_venues) == 0:
    response = {
                "count": len(filtered_venues),
                "data": [{
                        "id": None,
                        "name": "No Matching Venues Found",
                        }]
                }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================

@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):

  venueData = Venue.query.get(venue_id)
  showData = Show.query.filter(Show.venue_id == venue_id).all()

  def sortingPastShows(showData):
    upcomingShows = []
    pastShows = []
    currentDate = datetime.now()

    for s in showData:
      if currentDate > s["start_time"]:
        pastShows.append(s)
      else:
        upcomingShows.append(s)

    for x in upcomingShows:
      x["start_time"] = str(x["start_time"])
    for x in pastShows:
      x["start_time"] = str(x["start_time"])

    sorted_data = {
          "past_shows": pastShows,
          "upcoming_shows": upcomingShows,
          "past_shows_count": len(pastShows),
          "upcoming_shows_count": len(upcomingShows)
          }
    return sorted_data

  
  def creating_single_show_objects(showData):
    genres_and_shows = []
    objectShowData = []
    finalGenres = []
    allVenueGenres = ""
    for x in showData:
      currentArtist = Artist.query.get(x.artist_id)
      

      if currentArtist.genres[len(currentArtist.genres)-1] != " ":
        currentArtist.genres = currentArtist.genres + ", "

      allVenueGenres = allVenueGenres + currentArtist.genres

      singleShow = {
              "id": x.id,
              "artist_id": x.artist_id, 
              "venue_id": x.venue_id,
              "artist_name":  currentArtist.name,
              "artist_image_link": currentArtist.image_link,
              "start_time": x.start_time
              }
      objectShowData.append(singleShow)

    allVenueGenres = allVenueGenres.strip()
    if len(allVenueGenres) > 0:
      if allVenueGenres[len(allVenueGenres)-1] == ",":
        allVenueGenres = allVenueGenres[0:len(allVenueGenres)-1]

    allVenueGenres = allVenueGenres.split(",")

    for x in allVenueGenres:
      if x.strip() not in finalGenres:
        finalGenres.append(x.strip())
    
    genres_and_shows.append(finalGenres)
    genres_and_shows.append(objectShowData)
    return genres_and_shows


  all_venue_data = creating_single_show_objects(showData)
  sortedShowData = sortingPastShows(all_venue_data[1])
  

  formattedData = {
    "id": venueData.id,
    "name": venueData.name,
    "genres": all_venue_data[0],
    "address": venueData.address,
    "city": venueData.city,
    "state": venueData.state,
    "phone": venueData.phone  ,
    "website": venueData.website,
    "facebook_link": venueData.facebook_link,
    "seeking_talent": venueData.seeking_talent,
    "image_link": venueData.image_link,
    "past_shows": sortedShowData["past_shows"],
    "upcoming_shows": sortedShowData["upcoming_shows"],
    "past_shows_count": sortedShowData["past_shows_count"],
    "upcoming_shows_count": sortedShowData["upcoming_shows_count"] 
  }

  return render_template('pages/show_venue.html', venue=formattedData)

#  Create Venue
#  ----------------------------------------------------------------



# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # request.form.get('search_term', '').lower()
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  keys = request.form.items()
  genres = request.form.getlist('genres')
  cprint(genres, "Genres: ")
  form_data_formatted = {}
  for x in keys:
    form_data_formatted[x[0]] = x[1]
    # if x == 'genres':

  separator = ", "

  form_data_formatted["genres"] = separator.join(genres)


  cprint(form_data_formatted, "Form Data Formatted: ")

  try:
    newVenue = Venue(name=form_data_formatted["name"], city=form_data_formatted["city"], state=form_data_formatted["state"], address=form_data_formatted["address"], phone=form_data_formatted["phone"], facebook_link=form_data_formatted["facebook_link"], website=form_data_formatted["website"], image_link=form_data_formatted["image_link"]) 
    db.session.add(newVenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('It appears there was an issue creating ' + request.form['name'] + ".")
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None




#  Artists
#  ----------------------------------------------------------------

# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================

@app.route('/artists')
def artists():
  artistData = db.session.query(Artist.id, Artist.name).all()

  def format_data(data):
    full_list = []
    for x in data:
      single_artist = {}
      single_artist["id"] = x[0]
      single_artist["name"] = x[1]
      full_list.append(single_artist)
    return full_list

  full_list = format_data(artistData)

  cprint(full_list, "Full List: ")

  return render_template('pages/artists.html', artists=full_list)



# ===================================================================================================
#     =====================================  TO DO  =====================================
# ===================================================================================================

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))




# ===================================================================================================
#     =====================================  COMPLETED  =====================================
# ===================================================================================================

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }

  single_artist = Artist.query.get(artist_id)
  formatted_genres = cfunc.format_genre_to_list(single_artist.genres)


  
  
  formatted_artist_data = cfunc.format_to_object(str(single_artist).split(", \""))
  sorted_shows = sortingPastShows(creating_single_show_objects(Show.query.filter(Show.artist_id == artist_id).all())[1])
  formatted_artist_data["past_shows"] = sorted_shows["past_shows"]
  formatted_artist_data["upcoming_shows"] = sorted_shows["upcoming_shows"]
  formatted_artist_data["past_shows_count"] = sorted_shows["past_shows_count"]
  formatted_artist_data["upcoming_shows_count"] = sorted_shows["upcoming_shows_count"]
  formatted_artist_data["genres"] = formatted_genres
  cfunc.add_venue_data(formatted_artist_data, Venue, "upcoming_shows", "venue_id")
  cfunc.add_venue_data(formatted_artist_data, Venue, "past_shows", "venue_id")

  cprint(formatted_artist_data, "formatted_artist_data")


  # data = list(filter(lambda d: d['id'] == artist_id, [data3]))[0]
  return render_template('pages/show_artist.html', artist=formatted_artist_data)

#  Update
#  ----------------------------------------------------------------

# ===================================================================================================
#     =====================================  TO DO  =====================================
# ===================================================================================================


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
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

  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
