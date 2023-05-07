# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine,reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    last_year_precip = session.query(measurement.date, measurement.prcp)\
              .filter(measurement.date >= year_ago, measurement.prcp != None)\
              .order_by(measurement.date).all()
    rain_totals = []
    for entry in last_year_precip:
        row = {}
        row["date"] = last_year_precip[0]
        row["prcp"] = last_year_precip[1]
        rain_totals.append(row)

    return jsonify(rain_totals)
session.close()



@app.route("/api/v1.0/stations")
def stations():
    stations_query = session.query(station.name, station.station)
    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(stations.to_dict())


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of temperatures for prior year"""
#    * Query for the dates and temperature observations from the last year.
#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
#           * Return the json representation of your dictionary.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    year_temp = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= year_ago, measurement.station == 'USC00519281').\
        order_by(measurement.date).all()
    
    temperature_totals = []
    for temp in year_temp:
        row = {}
        row["date"] = year_temp[0]
        row["tobs"] = year_temp[1]
        temperature_totals.append(row)

    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def beginning(start):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)
if __name__ == '__main__':
    app.run(debug=True)


@app.route("/api/v1.0/<start>/<end>")
def second(start,end):
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)