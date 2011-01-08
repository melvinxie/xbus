from django.shortcuts import render_to_response
from django.utils import translation

def index(request):
    translation.activate('en')
    return render_to_response('index.html', {'mobile': request.mobile})
