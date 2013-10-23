__author__ = 'Jo'

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render
#from models import Vote
from django.http import Http404


def index(request):
    return render_to_response("index.html")


def welcome(request):
    if request.method == 'POST': # If the form has been submitted...
        email = request.session.get('email')
        password = request.session.get('password')
        #Check authenticated
        #If  ok
        return HttpResponseRedirect("/dashboard") # Redirect after POST
        #If not authenticated
        #inform
    else:
        return render(request, "welcome.html")


def welcome_account(request):
    return render_to_response("welcome_account.html")


def welcome_train(request):
    return render_to_response("welcome_train.html")


def welcome_categories(request):
    return render_to_response("welcome_categories.html")


def create_query(request):
    return render_to_response("create_query.html")


def home(request):
    return render_to_response("home.html")


def analytics(request):
    return render_to_response("analytics.html")


def results(request, query_id):
    try:
        query_id = str(query_id)
    except ValueError:
        raise Http404()
    return render_to_response("results.html", {"query_name": query_id})


def test(request):
    return render_to_response("legend-template.html")