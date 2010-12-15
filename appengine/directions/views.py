from datetime import time
from directions.models import Direction
from django.shortcuts import render_to_response
from stations.models import station_id_map

def direction(request):
    from_station = request.GET['from_station']
    to_station = request.GET['to_station']
    day = request.GET['day']
    now = time(int(request.GET['hour']), int(request.GET['minute']))
    from_id = station_id_map[from_station]
    to_id = station_id_map[to_station]
    results = Direction().search(from_id, to_id, day, now)
    return render_to_response('directions/direction.html',
                              {'results': results, 'goal': to_station})
