from django.shortcuts import render_to_response
from django.utils import translation

# TODO: Move out timetable unrelated views

def index(request):
    translation.activate('ja')
    return render_to_response('index.html', {'mobile': request.mobile})

def english(request):
    translation.activate('en')
    return render_to_response('index.html', {'mobile': request.mobile})
