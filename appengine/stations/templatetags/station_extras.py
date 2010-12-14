from django import template
from django.utils.safestring import mark_safe

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
