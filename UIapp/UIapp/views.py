__author__ = 'Jo'

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.http import Http404
from initialiaze_repo import initialize
from models import Category, Team, Project, Category_value, Query, Query_properties, Results
from django.contrib.auth.models import Group, User
import urllib2
import json
from django.core import serializers
from collections import namedtuple
import datetime, time


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
    titles = ['Name', 'Keywords', 'Usernames', 'Created by', 'From', 'To', 'Created']
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
        query_response['Keywords'] = dynamic_properties["Keywords"]
        query_response['Usernames'] = dynamic_properties["Usernames"]
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
    data = []
    categories_counter = []
    positive_counter = 0
    negative_counter = 0
    neutral_counter = 0
    try:
        #query_id = str(query_id)
        #Must store the response, if there is no reponse, otherwise return the stored one.
        # IF NOT STORED
        query = Query.objects.get(id=query_id)
        results = Results.objects.filter(query=query)
        #run for all categories
        properties = get_query_properties(query)
        all_properties = ''
        # Get all properties
        for property in properties.keys():
            all_properties += '+(%s) ' % properties[property]

        if results: #bring it from the database
            response = results.__getitem__(0).results
            response = json.loads(response)
            #print response
        else: #make a new query
            query_all = '{"query":{"bool":{"must":[{"query_string":{"query":"%s"}},{"term":{"doc.lang":"en"}},{"range":{"doc.created_at":{"from":"%s","to":"%s"}}}]}},"from":0,"size":1000, "sort":["_score"]}' % (
                all_properties, int(time.mktime(query.from_date.timetuple()) * 1000),
                int(time.mktime(query.to_date.timetuple()) * 1000))
            response = parse_query_for_sentiments(query_all)
            #print "Got response: %s " %response
            newResponse = Results(query=query, results=json.dumps(response), updated=datetime.datetime.now())
            #print "Stored object"
            newResponse.save()
            #print response
        #count the occurrences in response
        for property in properties.keys():
            list = properties[property].split(",")
            word_counter = []
            for word in list:
                number = json.dumps(response).count(word)
                text = '{"name":"%s","times":"%s"}' % (word, number)
                word_counter.append(json.loads(text))
                print " The property %s in list of properties %s has been found %s times" % (word, property, number)
            text={}
            text["category"]=property
            text["properties"]=word_counter
            #text = '{"category":"%s","properties":"%s"}' % (property, word_counter)
            categories_counter.append(text)
            #categories_counter.append(property)
            #categories_counter.append(word_counter)

        print categories_counter

        for message in response:
            if message["_score"] > 0.05:
                data.append(message["_source"]["doc"])
                #print "Just Added: %s" %message["_source"]["doc"]
                try:
                    if message["_source"]["doc"]["senti_tag"] == "positive":
                        positive_counter += 1

                    elif message["_source"]["doc"]["senti_tag"] == "negative":
                        negative_counter += 1

                    elif message["_source"]["doc"]["senti_tag"] == "neutral":
                        neutral_counter += 1
                        #print "Found a message with tag: " % message["_source"]["doc"]
                except:
                    #print "No sentiment tag for message %s" %message["_source"]["doc"]
                    continue

    except ValueError:
        print ValueError.message
        raise Http404()
        #for i in data:
    #    print i
    return render_to_response("results.html", {"query_name": query.name, "response": data, "positive": positive_counter,
                                               "negative": negative_counter, "neutral": neutral_counter,
                                               "categories": categories_counter})


def test(request):
    return render_to_response("legend-template.html")


def search(request):
    return render_to_response("search.html")

# Get all the properties for a query
def get_query_properties(query):
    query_properties = Query_properties.objects.filter(query=query)
    results = {}
    #usernames = ' '
    for query_property in query_properties:
        results[str(query_property.category.name)] = str(query_property.properties)
        # if query_property.category.name == 'Keywords':
        #     keywords = query_property.properties
        # elif query_property.category.name == 'Twitter':
        #     usernames = '%s %s' % (usernames, query_property.properties)
        # elif query_property.category.name == 'Facebook':
        #     usernames = '%s %s' % (usernames, query_property.properties)

    #result = {"Keywords": keywords, "Usernames": usernames}
    #print result
    return results


def parse_query_for_sentiments(query):
    #query='{"query":{"bool":{"must":[{"query_string":{"query":"+(%s) +(%s)"}},{"term":{"doc.lang":"en"}},{"range":{"doc.created_at":{"from":"%s","to":"%s"}}}]}},"from":0,"size":6000, "sort":["_score"]}' %(properties["Keywords"],properties["Usernames"], int(time.mktime(query.from_date.timetuple())*1000), int(time.mktime(query.to_date.timetuple())*1000))
    response = urllib2.urlopen(
        'http://83.212.114.237:9200/twitter/_search',
        query
    )
    response = response.read()
    response = json.loads(response)["hits"]["hits"]
    return response