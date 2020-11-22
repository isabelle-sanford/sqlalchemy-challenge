import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.measurement

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start date]<br/>"
        f"/api/v1.0/[start date]/[end date]<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation by date"""
    # Query all passengers
    q = (
        Query(Measurement)
        .with_session(session)
        .with_entities(Measurement.date, Measurement.prcp)
        .all()
    )
    results = {k:v for k,v in q}

    session.close()

    return jsonify(results)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations in the dataset"""
    # Query 
    q = (
        Query(Measurement)
        .with_session(session)
        .with_entities(Measurement.station.distinct())
        .all()
    )

    results = list(np.ravel(q))
    session.close()

    return jsonify(results)


@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temps from most active station in last year"""
    year_ago = dt.datetime(2016, 8, 23) # fix later
    stats = (
        Query(Measurement)
        .filter(Measurement.date > year_ago)
        .with_session(session)
        .with_entities(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .all()
    )
    active = max({k:v for k,v in stats})
    
    
    # Query 
    q = (
        Query(Measurement)
        .filter(Measurement.station == active)
        .with_session(session)
        .with_entities(Measurement.date, Measurement.tobs)
        .all()
    )


    session.close()

    return jsonify(q) # do I really not need to do anything to q?




@app.route("/api/v1.0/<start>")
def summary_start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of """
    # Query 
    q = (
        Query(Measurement)
        .filter(Measurement.date >= start)
        .with_session(session)
        .with_entities(Measurement.date,
                       func.min(Measurement.tobs), 
                       func.max(Measurement.tobs), 
                       func.avg(Measurement.tobs))
        .all()
    )
    results = {y[0]:{"TMin":y[1], "TMax":y[2], "TAvg":y[3]} for y in q}
    
    session.close()

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def summary_startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of """
    # Query 
    q = (
        Query(Measurement)
        .filter(Measurement.date >= start,
               Measurement.date <= end)
        .with_session(session)
        .with_entities(Measurement.date,
                       func.min(Measurement.tobs), 
                       func.max(Measurement.tobs), 
                       func.avg(Measurement.tobs))
        .all()
    )
    results = {y[0]:{"TMin":y[1], "TMax":y[2], "TAvg":y[3]} for y in q}
    
    session.close()

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
