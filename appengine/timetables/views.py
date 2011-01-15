from django.shortcuts import render_to_response
from django.utils import translation

# TODO: Move out timetable unrelated views

def index(request):
    return render_to_response('index.html', {'mobile': request.mobile})

def english(request):
    translation.activate('en')
    return index(request)
