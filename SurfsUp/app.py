# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Create root route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )
# Define a function which calculates and returns the date one year from the most recent date
def get_one_year_ago():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    return one_year_ago

# Create a route that queries precipitation levels and dates and returns
# a dictionary using date as key and precipitation as value
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation (prcp)and date (date) data"""

    # Calculate date 12 months ago
    one_year_ago = get_one_year_ago()

    # Query
    last_12months_precp = session.query(Measurement.date, Measurement.prcp). \
        filter(Measurement.date >= one_year_ago).all()

    # Close session
    session.close()

    # Create Dictionary
    precipitation_data = {}
    for date, prcp in last_12months_precp:
        precipitation_data[date] = prcp

        return jsonify(precipitation_data)


# Create station route of a list of the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():
    # Create the session
    session = Session(engine)

    # Query stations
    stations = session.query(Station.name, Station.station).all()

    # Close session
    session.close()

    # Create a list of dictionaries of stations
    station_data = [{"name": name, "station": station} for name, station in stations]

    # Return the list as JSON
    return jsonify({"stations": station_data})

# Define a function which calculates and returns the date one year from
# the most recent date of the most active stations
def get_another_year_ago():
    # Create a new session
    session = Session(engine)

    # Query the most recent date of the most active station
    most_recent_active_dt = session.query(Measurement.date). \
        filter(Measurement.station == "USC00519281").order_by(Measurement.date.desc()).first()[0]

    # Close session
    session.close()

    # Calculate one year ago from the most recent date
    another_year_ago = dt.datetime.strptime(most_recent_active_dt, '%Y-%m-%d') - dt.timedelta(days=365)
    return another_year_ago


# Create a route that queries temperature data from the most-active station in the last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
     session = Session(engine)

    #Calculate date 12 months ago
     another_year_ago = get_another_year_ago()

     last_12months_temp = session.query(Measurement.date, Measurement.tobs).\
     filter(Measurement.date >= another_year_ago).filter(Measurement.station == "USC00519281").all()

     # Close session
     session.close()

      # Create a list of dictionaries for temperature data
     temperature_data = [{"date": date, "temperature": tobs} for date, tobs in last_12months_temp]

     # Return the list as JSON
     return jsonify({"temperature_data": temperature_data})

# Define a function to calculate temperature statistics for a given date range
def calculate_temps(start_date, end_date=None):
    # Create our session
    session = Session(engine)

    if end_date:
        # Query for date range
        temperature_range = session.query(func.min(Measurement.tobs).label('min_temp'),
                                          func.avg(Measurement.tobs).label('avg_temp'),
                                          func.max(Measurement.tobs).label('max_temp')). \
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        # Query for start date only
        temperature_range = session.query(func.min(Measurement.tobs).label('min_temp'),
                                          func.avg(Measurement.tobs).label('avg_temp'),
                                          func.max(Measurement.tobs).label('max_temp')). \
            filter(Measurement.date >= start_date).all()

    # Close session
    session.close()

    # Extract the result
    result = temperature_range[0]

    # Create a dictionary with the result
    temperature_result = {
        "min_temperature": result.min_temp,
        "avg_temperature": result.avg_temp,
        "max_temperature": result.max_temp
    }

    return temperature_result


# Define the route for /api/v1.0/<start>
@app.route("/api/v1.0/<start>")
def start(start_date):
    # Create our session
    session = Session(engine)

    # Call the calculate_temps function with start date
    result = calculate_temps(start)

    # Close session
    session.close()

    # Return the result as JSON
    return jsonify(result)

# Define the route for /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def start_end(start_date, end_date):
    # Create our session
    session = Session(engine)

    # Call the calculate_temps function with start and end dates
    result = calculate_temps(start, end)

    # Close session
    session.close()

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)