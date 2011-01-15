from google.appengine.ext import db
import csv
import math

stations = {}
station_id_map = {}
for id, name, english, latitude, longitude in csv.reader(open('stations.csv')):
    name = unicode(name, 'utf-8')
    stations[id] = (name, float(latitude), float(longitude), english)
    station_id_map[name] = id
"""
for station in Station.all():
    stations[station.key().id()] = (
            station.name, station.latitude, station.longitude)
    station_id_map[station.name] = station.key().id()
"""

class Station(db.Model):
    name = db.StringProperty(required=True)
    latitude = db.FloatProperty()
    longitude = db.FloatProperty()

    @classmethod
    def distance(cls, a, b):
        return calc_distance(stations[a][1], stations[a][2],
                             stations[b][1], stations[b][2])

nauticalMilePerLat = 60.00721
nauticalMilePerLongitude = 60.10793
rad = math.pi / 180.0
metersPerNauticalMile = 1852.0
def calc_distance(lat1, lon1, lat2, lon2):
    """
    Caclulate distance between two lat lons in NM
    """
    yDistance = (lat2 - lat1) * nauticalMilePerLat
    xDistance = (math.cos(lat1 * rad) + math.cos(lat2 * rad)) * \
                    (lon2 - lon1) * (nauticalMilePerLongitude / 2)
    distance = math.sqrt( yDistance**2 + xDistance**2 )
    return int(distance * metersPerNauticalMile)
