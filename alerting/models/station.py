import json
import urllib2
from datetime import datetime

from flask.ext.mongokit import Document

from alerting import db, app

from shapely.wkt import loads
from shapely.geometry import Point

class Station(Document):
    __collection__ = 'stations'
    use_schemaless = True
    use_dot_notation = True
    structure = {
        'description'       : unicode,  
        'latitude'          : float,
        'longitude'         : float,
        'geometry'          : unicode, # WKT of the feature
        'timeseries'        : dict, # Data for the station
        'last_obs'          : dict, # Simple access to most recent data
        'link'              : unicode, # External link to station metadata page
        'type'              : unicode,
        'provider'          : unicode, # Provider of the station (USGS, NDBC, etc.)
        'created'           : datetime,
        'updated'           : datetime
    }
    required_fields = ['latitude', 'longitude', 'geometry','timeseries','provider','created', 'updated']
    default_values = { 'created': datetime.utcnow, 'updated': datetime.utcnow }

    def coordinates(self):
        try:
            geo = loads(self.geometry)
            if isinstance(geo, Point):
                return (geo.coords[0][1], geo.coords[0][0])
            else:
                raise ValueError("Not a point")
        except:
            return None

db.register([Station])


def parse_stations():
    url = "http://explorer.glos.us/getObs.php"
    j = json.loads(urllib2.urlopen(url).read())
    for s in j:
        properties = s.get('properties')
        provider = properties.get('provider')
        description = properties.get('descr')
        station = db.Station.find_one( { 'provider' : provider, 'description' : description })
        if station is None:
            station = db.Station()
            station.provider = provider
            station.description = description

        station.latitude = float(properties.get("lat"))
        station.longitude = float(properties.get("lon"))
        station.geometry = unicode(Point(station.longitude, station.latitude).wkt)
        station.timeseries = properties.get("timeSeries")
        station.last_obs = properties.get("topObs")
        station.link = properties.get("url")
        station.type = properties.get("siteType")
        station.updated = datetime.utcnow()

        station.save()

        
