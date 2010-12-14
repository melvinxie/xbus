# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.filter
def route_time(time):
    return '%s:%s' % (time[0], str(time[1]).zfill(2))

@register.filter
def total_time(time):
    text = u'約'
    if time[0]:
        text += u'%s時間' % time[0]
    if time[1]:
        text += u'%s分' % time[1]
    return text
