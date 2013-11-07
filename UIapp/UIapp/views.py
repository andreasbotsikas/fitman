__author__ = 'Jo'

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import Http404
from initialiaze_repo import initialize
from models import Category, Team, Project, Category_value, Query, Query_properties
from django.contrib.auth.models import Group, User
import urllib2
import json
from django.core import serializers
from collections import namedtuple


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
    current_project = Project.objects.latest("created")
    # print current_project.name # debug
    # queries
    queries = Query.objects.filter(owned_by=current_project.id)
    list_of_queries = []
    titles = ['Name', 'Keywords', 'Usernames','Created by', 'From', 'To', 'Created']
    for query in queries:
        query_response = {}
        query_response['id'] = query.id
        query_response['Name'] = query.name
        query_response['Created_by'] = query.created_by.username
        query_response['From'] = query.from_date
        query_response['To'] = query.to_date
        query_response['Created'] = query.created

        #query_response= "{'id':'%s','Name': '%s'" %(query.id, query.name)
        dynamic_properties = get_query_properties(query)
        query_response['Keywords'] = dynamic_properties ["Keywords"]
        query_response['Usernames'] = dynamic_properties ["Usernames"]
        #print "The property name is:%s" % query_response['Keywords']

        # query_properties = Query_properties.objects.filter(query=query)
        # for query_property in query_properties:
        #     print "The property object is:%s" %query_property.category.name
        #     # a Category that must a appear in the table header
        #     #if query_property.category.name not in titles:
        #         #titles.append("%s" % query_property.category.name)
        #     # add the property name & value to the response
        #     if query_property.category.name=='Keywords':
        #         #query_response += ",'%s':%s"%(query_property.category.name, query_property.properties)
        #         query_response['Keywords']=query_property.properties
        #         print "The property name is:%s" %query_property.properties
        list_of_queries.append(query_response)
    return render_to_response("home.html", {"headers": titles, "content": list_of_queries})


def analytics(request):
    return render_to_response("analytics.html")


def results(request, query_id):
    #if authorized
    #MUST DEVELOP
    """

    :param request:
    :param query_id:
    :return: :raise:
    """
    try:
        #query_id = str(query_id)
        #Must store the response, if there is no reponse, otherwise return the stored one.
        # IF NOT STORED
        query = Query.objects.filter(id=query_id)
        properties = get_query_properties(query)
        #print properties["Keywords"]
        #print properties["Usernames"]
        #must put it into settings
        req = urllib2.Request('http://83.212.114.237:9200/twitter/_search?pretty')
        req.add_header('-d',
                       '{"size":1000,"facets":{},"query":{"bool":{"must":[{"query_string":{"query":"%s","default_field":"couchbaseDocument.doc.text"}}],"should":[{"query_string":{"query":"%s","default_field":"_all"}}],"must_not":[]}},"sort":[],"from":0}' % (
                           properties["Keywords"], properties["Usernames"]))
        resp = urllib2.urlopen(req)
        response=resp.read()
        #   parse the response for easier handlying on the template
        # -- Insert messages in the table
        response=json.loads(response)["hits"]["hits"]
        data=[]
        positive_counter=0
        negative_counter=0
        neutral_counter=0
        for message in response:
            data.append(message["_source"]["doc"])
            try:
                if message["_source"]["doc"]["senti_tag"] == "positive":
                    positive_counter+=1
                elif message["_source"]["doc"]["senti_tag"] == "negative":
                    negative_counter+=1
                elif message["_source"]["doc"]["senti_tag"] == "neutral":
                    neutral_counter+=1
            except:
                print "No sentiment tag for message %s" %message["_source"]["doc"]

    except ValueError:
        raise Http404()
    return render_to_response("results.html", {"query_name": query_id, "response":data, "positive":positive_counter, "negative":negative_counter, "neutral":neutral_counter})


def test(request):
    return render_to_response("legend-template.html")

# Get all the properties for a query
def get_query_properties(query):
    query_properties = Query_properties.objects.filter(query=query)
    usernames = ' '
    for query_property in query_properties:
        #print "The property object is:%s" % query_property.category.name
        # a Category that must a appear in the table header
        #if query_property.category.name not in titles:
        #titles.append("%s" % query_property.category.name)
        # add the property name & value to the response
        if query_property.category.name == 'Keywords':
            keywords = query_property.properties
        elif query_property.category.name == 'Twitter':
            usernames = '%s %s' %(usernames,query_property.properties)
        elif query_property.category.name == 'Facebook':
            usernames = '%s %s' %(usernames,query_property.properties)
    result = {"Keywords": keywords, "Usernames": usernames}
    #print result
    return result