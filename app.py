import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)
session = scoped_session(sessionmaker(bind=engine))
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<end><br/>"
        f"For the last two routes, enter a start date and range date, respectivily, in the 'yyyy-mm-dd' format"


    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of precipitation"""

    #Query to call date and precipitation data 
    ### Get the last data point 
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ### Since the latest date is the first element in the tuple, it needs to be extracted from the tuple
    maxdate = max_date[0]

    ### Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.datetime.strptime(maxdate, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    query_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # Convert list of tuples into dictionary
    dict_prcp = dict(query_prcp)

    # jsonify the dictionary
    return jsonify(dict_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Docstring
    """JSON list of stations from the dataset"""

    # Query the stations
    active_stations = session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples to list
    list_stations = list(np.ravel(active_stations))

    # Jsonify the list
    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Docstring
    """JSON list of temperature observations for the last 366 days"""

    # Query to get the precipitation data 
     ### Get the last data point 
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    ### Since the latest date is the first element in the tuple, it needs to be extracted from the tuple
    maxdate = max_date[0]

    ### Calculate the date 1 year ago from the last data point in the database
    prev_year = dt.datetime.strptime(maxdate, "%Y-%m-%d") - dt.timedelta(days=366)

    ## Query
    query_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    # Convert list of tuples into list
    list_tobs = list (query_tobs)

    #Jsonify the list
    return jsonify(list_tobs)


@app.route("/api/v1.0/<start>")
def start(start = None):
    # Docstring
    """JSON list of tmin, tmax, tavg for the dates greater than/equal to date entered"""
    
    # Query start date
    query_startdate = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # Convert list of tuples into list
    list_startdate = list(query_startdate)

    # Jsonify the list
    return jsonify(list_startdate)

@app.route("/api/v1.0/<start>/<end>")
def end(start = None, end = None):
    # Docstring
    """JSON list of tmin, tmax, tavg for the dates in between of start date and end date included (range)"""

    if end ==None: 
        end1 = end = session.query(func.max(Measurement.date)).first()[0]
    # Query
    query_rangedates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    #Convert list of tuples into list
    list_rangedates = list(query_rangedates)
    
    # Jsonify the list
    return jsonify(list_rangedates)

if __name__ == '__main__':
    app.run(debug=True)