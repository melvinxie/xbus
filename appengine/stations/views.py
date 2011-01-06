from django.shortcuts import render_to_response
from heapq import nsmallest
from stations.models import Station, stations, calc_distance
import csv

def nearby(request):
    latitude = float(request.GET['lat'])
    longitude = float(request.GET['lng'])
    station_dists = [(calc_distance(latitude, longitude,
                                    station[1], station[2]), station)
                     for station in stations.itervalues()]
    nearby_stations = [[i + 1, item[0], item[1]]
                       for i, item in enumerate(nsmallest(5, station_dists))]
    map_url = 'http://maps.google.com/maps/api/staticmap?size=300x300&sensor=true&mobile=true&markers=color:blue|%f,%f' % (latitude, longitude)
    for i, dist, station in nearby_stations:
        map_url += '&markers=color:red|label:%d|%f,%f' % (i,
                station[1], station[2])
    return render_to_response('stations/nearby.html',
                              {'nearby_stations': nearby_stations,
                               'map_url': map_url})

def create(request):
    for id, name, latitude, longitude in csv.reader(open('stations.csv')):
        s = Station.get_by_id(int(id))
        if s:
            s.name = unicode(name, 'utf-8')
            s.latitude = float(latitude)
            s.longitude = float(longitude)
            s.save()

reading_map = {}
def list(request, key):
    if not reading_map:
        for row in csv.reader(open('readings.csv')):
            init = unicode(row[0], 'utf-8')
            reading = unicode(row[1], 'utf-8')
            station = unicode(row[2], 'utf-8')
            if init not in reading_map:
                reading_map[init] = []
            reading_map[init].append((reading, station))
    return render_to_response('stations/list.html',
                              {'stations': reading_map[key]})
