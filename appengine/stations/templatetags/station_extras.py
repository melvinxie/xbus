from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

register = template.Library()

@register.filter
def section(stations, autoescape=None):
    result = ''
    prev = ''
    for reading, station in stations:
        if reading != prev:
            result += '<li class="sep">%s</li>' % reading
            prev = reading
        result += '<li><a href="#" onclick="fill(\'%s\')">%s</a></li>' % \
                (station, station)
    return mark_safe(result)

@register.filter
def name(station):
    if get_language() == 'en':
        return '%s %s' % (station[3], station[0])
    else:
        return station[0]
