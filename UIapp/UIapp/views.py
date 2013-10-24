__author__ = 'Jo'

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import Http404
from initialiaze_repo import initialize
from models import Category, Team, Project, Category_value, Query, Query_properties
from django.contrib.auth.models import Group,User



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
        #for development mode only!!
        initialize()
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
    # get the authenicated user instead
    # user = User.objects.filter(username="test1").latest('get_latest_by'=id)
    # teams = Team.objects.filter(created_by=user)
    # # to be selected by the user
    # current_team=teams.latest()
    # projects=Project.objects.filter(owned_by=current_team.name, created_by=user.username)
    current_project=Project.objects.latest("created")
    # print current_project.name # debug
    # queries
    queries=Query.objects.filter(owned_by=current_project.id)
    list_of_queries=[]
    titles=['Name','Keywords','Created by', 'From', 'To','Created']
    for query in queries:
        query_response={}
        query_response['id']=query.id
        query_response['Name']=query.name
        query_response['Created_by']=query.created_by.username
        query_response['From']=query.from_date
        query_response['To']=query.to_date
        query_response['Created']=query.created

        #query_response= "{'id':'%s','Name': '%s'" %(query.id, query.name)
        query_properties = Query_properties.objects.filter(query=query)
        for query_property in query_properties:
            print "The property object is:%s" %query_property.category.name
            # a Category that must a appear in the table header
            #if query_property.category.name not in titles:
                #titles.append("%s" % query_property.category.name)
            # add the property name & value to the response
            if query_property.category.name=='Keywords':
                #query_response += ",'%s':%s"%(query_property.category.name, query_property.properties)
                query_response['Keywords']=query_property.properties
                print "The property name is:%s" %query_property.properties
        list_of_queries.append(query_response)
    return render_to_response("home.html", {"headers":titles, "content":list_of_queries})


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




