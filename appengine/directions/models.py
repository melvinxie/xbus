# -*- coding: utf-8 -*-

from datetime import date, datetime, time, timedelta
from django.utils import simplejson
from heapq import heappush, heappop
from stations.models import stations, station_id_map
from timetables.models import duration, get_day, TimeTable

def plus(t, d):
    hour, minute = divmod(t[0] * 60 + t[1] + d, 60)
    hour %= 24
    return hour, minute

class Direction(object):
    station_vmap, graph = simplejson.load(open('graph.json'))
    timetable_keys = simplejson.load(open('timetable_keys.json'))
    routes = {'TS02': u'\u7279\u53572', 'TS01': u'\u7279\u53571', 'T018':
            u'\u727918', 'T013': u'\u727913', '091': u'91', '093': u'93', '010':
            u'10', '011': u'11', '012': u'12', '013': u'13', '015': u'15',
            '016': u'16', '017': u'17', '018': u'18', '019': u'19', 'T081':
            u'\u727981', 'TW03': u'\u7279\u897f3', 'RW02': u'\u81e8\u897f2',
            '027': u'27', '026': u'26', '020': u'20', '022': u'22', '029':
            u'29', '028': u'28', 'T093': u'\u727993', 'M001': u'M1', '201':
            u'201', '032': u'32', '033': u'33', '031': u'31', '037': u'37',
            'RS05': u'\u81e8\u53575', 'K009': u'\u5feb\u901f9', '102': u'102',
            '046': u'46', '100': u'100', '101': u'101', '043': u'43', '042':
            u'42', 'T033': u'\u727933', 'T037': u'\u727937', '059': u'59',
            '055': u'55', '050': u'50', '051': u'51', 'N008': u'\u53178',
            'S005': u'\u53575', 'S001': u'\u53571', 'S003': u'\u53573', 'S002':
            u'\u53572', 'S008': u'\u53578', 'CK': u'\u76f4\u884c', '065': u'65',
            '067': u'67', '069': u'69', 'R': u'\u81e8', '075': u'75', '073':
            u'73', '070': u'70', '071': u'71', 'N003': u'\u53173', '078': u'78',
            'N001': u'\u53171', 'K205': u'\u5feb\u901f205', 'K202':
            u'\u5feb\u901f202', 'T008': u'\u72798', '203': u'203', '202':
            u'202', '205': u'205', '204': u'204', '207': u'207', '206': u'206',
            '208': u'208', '081': u'81', '080': u'80', '084': u'84', '003':
            u'3', '001': u'1', '006': u'6', '005': u'5', '004': u'4', '009':
            u'9', '008': u'8', 'R013': u'\u81e813', 'W008': u'\u897f8', 'W001':
            u'\u897f1', 'W003': u'\u897f3', 'W002': u'\u897f2', 'W005':
            u'\u897f5', 'W004': u'\u897f4', 'W006': u'\u897f6'}

    def search(self, s, t, day, now):
        # TODO: concurrency
        Direction.graph[s] = {}
        for route_key in Direction.station_vmap[s]['to']:
            Direction.graph[s]['%s-%s' % (s, route_key)] = (0, 0)
        Direction.graph[t] = {}
        for route_key in Direction.station_vmap[t]['from']:
            Direction.graph['%s-%s' % (t, route_key)][t] = (0, 0)
        # TODO: cache good paths
        dist, prev = self.dijkstra(Direction.graph, s, t)
        paths = sorted(self.paths(prev, s, t, set([t])), key=len)
        route_set = set()
        good_paths = []
        for path in paths:
            if len(path) > len(paths[0]) * 1.5 or len(good_paths) == 5:
                break
            else:
                routes = tuple(set(map(lambda v: v.split('-')[1].split('.')[0],
                                       path[1:-1])))
                if routes not in route_set:
                    route_set.add(routes)
                    good_paths.append(path)
        results = []
        for path in good_paths:
            time, result = self.sum_path(path, day, now)
            results.append({'time': time, 'path': result})
        del Direction.graph[s]
        del Direction.graph[t]
        for route_key in Direction.station_vmap[t]['from']:
            del Direction.graph['%s-%s' % (t, route_key)][t]
        return results

    def sum_path(self, path, day, now):
        result = []
        prev_route_key = ''
        total_time = 0
        route_time = 0
        # TODO: over = False
        for i in xrange(len(path[1:-1])):
            v1 = path[i + 1]
            v2 = path[i + 2]
            station_id, route_key = v1.split('-')
            if route_key != prev_route_key:
                route = {}
                route['station'] = stations[station_id][0]
                route['route'] = Direction.routes[route_key.split('.')[0]]
                link = '-'.join((v1, v2.split('-')[0]))
                if result:
                    if 'start' in result[-1]:
                        result[-1]['end'] = plus(result[-1]['start'],
                                                 route_time)
                        next_time = plus(result[-1]['end'], 1)
                    else:
                        result[-1]['time'] = route_time
                        next_time = plus((now.hour, now.minute), route_time)
                    now = time(next_time[0], next_time[1])
                if link in Direction.timetable_keys:
                    timetable = TimeTable.get_by_key_name(
                            Direction.timetable_keys[link])
                    route['way'] = '(' + timetable.name + ')'
                    start = timetable.next_time(now, day)
                    if start:
                        route['start'] = start
                route_time = 0
                prev_route_key = route_key
                result.append(route)
            route_time += Direction.graph[v1][v2][1]
            total_time += Direction.graph[v1][v2][1]
        if 'start' in result[-1]:
            result[-1]['end'] = plus(result[-1]['start'], route_time)
        else:
            result[-1]['time'] = route_time
        if 'start' in result[0] and 'end' in result[-1]:
            total_time = duration(result[0]['start'], result[-1]['end'])
        else:
            total_time = divmod(total_time, 60)
        return total_time, result

    def dijkstra(self, g, s, t):
        dist = {s: 0}
        prev = {s: set()}
        visited = set()
        q = []
        heappush(q, (0, s))
        while q:
            v = heappop(q)[1]
            if t in dist and dist[v] > dist[t]:
                break
            if v not in visited:
                visited.add(v)
                for u, w in g[v].iteritems():
                    d = dist[v] + w[0]
                    if u not in dist or d < dist[u]:
                        dist[u] = d
                        prev[u] = set([v])
                        heappush(q, (d, u))
                    elif d == dist[u]:
                        prev[u].add(v)
        return dist, prev

    def paths(self, prev, s, t, visited):
        if t == s:
            return [[s]]
        else:
            results = []
            for v in prev[t]:
                if v not in visited:
                    visited.add(v)
                    for path in self.paths(prev, s, v, visited):
                        results.append(path + [t])
                    visited.remove(v)
            return results
