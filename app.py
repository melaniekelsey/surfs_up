#from flask import Flask
#app = Flask(__name__)
#@app.route('/')
#def hello_world():
    #return 'Hello world'
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Setting up database engine connecting to the sqlite db
engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect our database
Base = automap_base()
Base.prepare(engine, reflect=True)

#Save and create references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create a session link from Python to our DB
session = Session(engine)

#Creating a new Flask instance called app. The name variable denotes the name of the current function
app = Flask(__name__)
#Creating a route and define the starting point the / deontes we want our data at the root of our routes
@app.route("/")

#Welcome route or homepage with return statements referencing all the other routes
#Use the naming convention of /api/v1.0/ to signify this is version one of our application
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')
#Setting up route for precipitation data
@app.route("/api/v1.0/precipitation")

#Creating precipitation function adding date that calcs date one year ago
#Next write a query that gets date and prcp for the previous year
#Next we created a dictionary with date as key and prcp as the value to jsonify our dictionary
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)

#Creating the stations route 
#Create a function called stations() that creates a query to pull all stations into a DB
#Next we add list(np.ravel(results)) to unravel our results into a 1D array and convert to a list
#Next we jsonify that list and return it as a jSON
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#Creating the total obs route
#Create a function called temp_monthly that calcs date one year ago
#Next it queries the primary station for all temp obs from the previous year
#Next it unravels the results into a 1D array and converts it to a list
#Next we jsonify that list and return it as a JSON
@app.route("/api/v1.0/tobs")
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#Creating a route for the Statistics
#Create a function called stats with a start and end time of none for the time being
#Create a query called sel to select the min, avg and max temps from our SQLite DB
#To help determine the start and end date add the if-not statement to our code, that we will query the DB using the list just made
#and unravel the results into a 1D array and convert them to a list and then jsonify the results
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)
