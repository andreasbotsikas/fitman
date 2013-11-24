__author__ = 'Jo'

import urllib2
import json
import datetime
import time

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.http import Http404
from django.contrib.auth.models import Group, User
from django.utils import timezone
from django.core.context_processors import csrf
from dateutil import parser
from django.contrib.auth import authenticate, logout
from django import forms

from initialiaze_repo import initialize
from models import Category, Team, Project, Category_value, Query, Query_properties, Results
from updateSentimentKeys import multiple_values_update


def index(request):
    return render_to_response("index.html")


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/welcome")


def welcome(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        return HttpResponseRedirect("/dashboard") # Redirect after POST
    else:
        # Do something for anonymous users.
        print ('not autenticated')

    if request.method == 'POST': # If the form has been submitted...
        #email = request.session.get('email')
        #password = request.session.get('password')
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user = authenticate(username=email, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                print("User is valid, active and authenticated")
                #set user on session property to read it from results
            else:
                print("The password is valid, but the account has been disabled!")
                return HttpResponseRedirect("/") # Redirect after POST
        else:
            # the authentication system was unable to verify the username and password
            print("The username or password were incorrect.")
            return HttpResponseRedirect("/") # Redirect after POST

        #Check authenticated
        #If  ok
        return HttpResponseRedirect("/dashboard") # Redirect after POST
        #If not authenticated
        #inform
    else:
        #for development mode only!!
        initialize()
        return render(request, "welcome.html")

def signup(request):
    if request.method == 'POST': # If the form has been submitted...
        #email = request.session.get('email')
        #password = request.session.get('password')
        email=request.POST.get("email","")
        password=request.POST.get("password","")



        #Check authenticated
        #If  ok
        return HttpResponseRedirect("/welcome-categories") # Redirect after POST
        #If not authenticated
        #inform
    else:
        #for development mode only!!
        initialize()
        return render(request, "signup.html")

    return render_to_response("signup.html")

def welcome_account(request):
    if request.method == 'POST': # If the form has been submitted...
        #email = request.session.get('email')
        #password = request.session.get('password')
        email=request.POST.get("email","")
        password=request.POST.get("password","")
        user = authenticate(username=email, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                print("User is valid, active and authenticated")
                #set user on session property to read it from results
            else:
                print("The password is valid, but the account has been disabled!")
                return HttpResponseRedirect("/") # Redirect after POST
        else:
            # the authentication system was unable to verify the username and password
            print("The username or password were incorrect.")
            return HttpResponseRedirect("/") # Redirect after POST

        #Check authenticated
        #If  ok
        return HttpResponseRedirect("/dashboard") # Redirect after POST
        #If not authenticated
        #inform
    else:
        #for development mode only!!
        initialize()
        return render(request, "welcome.html")

    return render_to_response("welcome_account.html")


def welcome_train(request):
    return render(request, "welcome_train.html")


def welcome_categories(request):
    return render(request, "welcome_categories.html")


def create_query(request):
    if request.method == 'POST': # If the form has been submitted...
        ##Do not allow users to vote before a timeperiod has passed.
        #if request.session.get('has_voted', False):
        #        return HttpResponse("Wow, your mood changes fast! Try again in 30 seconds.")
        #request.session['has_voted'] = True
        #request.session.set_expiry(30) #60 secs
        user = User.objects.get(username="test1")
        print "user %s" % user
        #team = Team.objects.filter(name="AIDIMA-team")
        project = Project.objects.get(created_by=user)
        print "project %s" % project
        query_name = request.POST.get("query_name", "")
        print "name: %s" % query_name

        from_date = request.POST.get("datepicker_from", "")
        to_date = request.POST.get("datepicker_to", "")
        print "from date: %s" % from_date
        print "to date: %s" % to_date

        query = Query(name=query_name, venn="", from_date=parser.parse(from_date), to_date=parser.parse(to_date),
                      created=timezone.now(), created_by=user, owned_by=project)
        query.save()
        #print "query %s"%query
        keywords = request.POST.get("keywords", "")
        #print "keywords: %s"%keywords
        category = Category.objects.get(name="Keywords")
        query_property = Query_properties(query=query, category=category, properties=keywords)
        query_property.save()

        twitter = request.POST.get("twitter", "")
        #print "keywords: %s"%keywords
        category = Category.objects.get(name="Twitter")
        query_property = Query_properties(query=query, category=category, properties=twitter)
        query_property.save()

        brands = request.POST.get("brands", "")
        try:
            category = Category.objects.filter(name="brands")
        except ValueError:
            print ValueError.message
        if category.__len__(): #exists already the category
            #print category
            category = category[0]
        ## otherwise create the category
        else:
            print "is empty"
            category = Category(name="brands")
            category.save()
        query_property = Query_properties(query=query, category=category, properties=twitter)
        query_property.save()

        #form = ContactForm(request.POST) # A form bound to the POST data
        #if form.is_valid(): # All validation rules pass
        # Process the data in form.cleaned_data
        # ...

        ##handle dynamic properties
        i = 0;
        prop_value = "prop-value-%s" % i
        prop_name = "prop-name-%s" % i
        while request.POST.get(prop_value, ""):
            property_name = request.POST.get(prop_name, "")
            property_value = request.POST.get(prop_value, "")
            print property_name
            print property_value
            try:
                ## try to find if the category already exists - in lowercase
                category = Category.objects.filter(name=(str(property_name).lower()))
            except ValueError:
                print ValueError.message
                continue

            print category
            if category.__len__(): #exists already the category
                print category
                category = category[0]
            ## otherwise create the category
            else:
                print "is empty"
                category = Category(name=str(property_name).lower())
                category.save()
                ## end store the properties in the category
            query_property = Query_properties(query=query, category=category, properties=property_value)
            query_property.save()

            i += 1
            prop_value = "prop-value-%s" % i
            prop_name = "prop-name-%s" % i

        return HttpResponseRedirect("/dashboard") # Redirect after POST
    else:
        return render(request, 'create_query.html')
        #return render_to_response("create_query.html")


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
        if (dynamic_properties.get("Twitter")or dynamic_properties.get("twitter")):
            query_response['Usernames'] = dynamic_properties["Twitter"]
        if (dynamic_properties.get("Facebook") or dynamic_properties.get("facebook")):
            query_response['Usernames'] = dynamic_properties["Facebook"]
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
        ## Must store the response, if there is no reponse, otherwise return the stored one.
        ## IF NOT STORED
        query = Query.objects.get(id=query_id)
        results = Results.objects.filter(query=query)
        #run for all categories
        properties = get_query_properties(query)
        all_properties = ''
        # Get all properties
        for property in properties.keys():
            if len(properties)==1:
                all_properties += '%s' % properties[property]
            else:
                all_properties += '+(%s) ' % properties[property]

        if results: #bring it from the database
            response = results.__getitem__(0).results
            response = json.loads(response)
            print response
        else: #make a new query
            query_all = '{"query":{"bool":{"must":[{"query_string":{"query":"%s"}},{"term":{"doc.lang":"en"}},{"range":{"doc.created_at":{"from":"%s","to":"%s"}}}]}},"from":0,"size":6000, "sort":["_score"]}' % (
                all_properties, int(time.mktime(query.from_date.timetuple()) * 1000),
                int(time.mktime(query.to_date.timetuple()) * 1000))
            print query_all
            response = parse_query_for_sentiments(query_all)
            #print "Got response: %s " %response
            newResponse = Results(query=query, results=json.dumps(response), updated=datetime.datetime.now())
            #print "Stored object"
            newResponse.save()
            print response

        ## count the occurrences in response

        for property in properties.keys():
            list = properties[property].split(",")
            word_counter = []
            for word in list:
                number = json.dumps(response).count(word)
                text = '{"name":"%s","times":"%s", "sentiment":0}' % (word, number)
                word_counter.append(json.loads(text))
                #print " The property %s in list of properties %s has been found %s times" % (word, property, number)
            text = {}
            text["category"] = property
            text["properties"] = word_counter
            categories_counter.append(text)

        #print categories_counter


        for message in response:
            if message["_score"] > 0.05:
                data.append(message["_source"]["doc"])
                #print "Just Added: %s" %message["_source"]["doc"]
                try:
                    if message["_source"]["doc"]["senti_tag"] == "positive":
                        # for global metrics
                        positive_counter += 1
                        #print "Found a message with positive tag: %s " % json.dumps(message["_source"]["doc"])
                        # for mosaic diagram
                        for category in categories_counter:
                            for property in category["properties"]:
                                if (json.dumps(message["_source"]["doc"]["text"])).find(property["name"]) > 0:
                                    #print " Message with positive tag: %s : the found property is: %s"%(json.dumps(message["_source"]["doc"]), property["name"])
                                    pos_number = int(property["sentiment"]) + 1
                                    property["sentiment"] = pos_number

                    elif message["_source"]["doc"]["senti_tag"] == "negative":
                        negative_counter += 1
                        print "Found a message with negative tag: %s " % json.dumps(message["_source"]["doc"])
                        # for mosaic diagram
                        for category in categories_counter:
                            for property in category:
                                if (json.dumps(message["_source"]["doc"]["text"])).find(property["name"]) > 0:
                                    pos_number = int(property["sentiment"]) - 1
                                    property["sentiment"] = pos_number

                    elif message["_source"]["doc"]["senti_tag"] == "neutral":
                        neutral_counter += 1
                        #print "Found a message with tag: " % message["_source"]["doc"]
                except:
                    #print "No sentiment tag for message %s" %message["_source"]["doc"]
                    continue

                    #print categories_counter

    except ValueError:
        print ValueError.message
        raise Http404()
        #for i in data:
    #    print i

    return render(request, "results.html",
                  {"query_id": query.id, "query_name": query.name, "response": data, "positive": positive_counter,
                   "negative": negative_counter, "neutral": neutral_counter,
                   "categories": categories_counter})


def results_update(request):
    if request.method != 'POST': # If the form has been submitted...
        raise Http404('Only POST methods allowed')
    update_bulk = request.POST.get("retrain", "")
    ##send the bulk to the db service



    ##delete cashing from results, to get the updated ones from "results" methods
    results_id = request.POST.get("results-id", "")
    query = Query.objects.get(id=results_id)
    results = Results.objects.get(query=query)
    if results:
        results.delete()
        ## redirect to the proper page again
    path = "/queries/%s" % results_id
    return HttpResponseRedirect(path) # Redirect after update to the page


def results_delete(request, query_id):
    query = Query.objects.get(id=query_id)
    query.delete()
    return HttpResponseRedirect("/dashboard") # Redirect after update to the page


def test(request):
    return render_to_response("legend-template.html")


def search(request):
    return render_to_response("free-search.html")


def train(request):
    if request.method == 'POST': # If the form has been submitted...
        #must handle .csv
        csv=request.FILES.get("file","")
        #csv=request.FILES['file']
        file = request.FILES['file']
        print file
        #print file.content_type
        if file.content_type == 'text/csv':
            #response = urllib2.urlopen('http://83.212.114.237:9200/twitter/_search',file)
            req = urllib2.Request('http://83.212.114.237:8081/RA/public_process/sentimentTrain')
            req.add_header('-T',file)
            resp = urllib2.urlopen(req)
            response = resp.read()
            #print response
            return HttpResponseRedirect("/dashboard") # Redirect after POST

        #print file.read()
        #print file.name           # Gives name
        #print file.content_type   # Gives Content type text/html etc
        #print file.size           # Gives file's size in byte
        #print file.read()         # Reads file
        #print csv
        else:
            print "not valid file"
            return HttpResponseRedirect("/training") #

    else:
        return render(request,'training.html')

# Get all the properties for a query
def get_query_properties(query):
    query_properties = Query_properties.objects.filter(query=query)
    results = {}
    #usernames = ' '
    for query_property in query_properties:
            if str(query_property.properties) is "":
                continue
            else:
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


def user_based_sentiment(request):
    if request.method == 'GET':

        #http://localhost:8000/user_based_sentiment?sentiment_values='395902357026131968:positive,%20395901656044670976:positive,%20396550264318328832:negative,%20395902917976522752:negative,%20395902917976522752:na,'
        sentiment_values = request.GET.get("sentiment_values", "")

        if sentiment_values:

            sentiment_values = sentiment_values.replace(" ", "")

            sentiment_values = sentiment_values.split(",")

            if '' in sentiment_values:
                sentiment_values.remove('')
            lista = []

            for value in sentiment_values:
                res = value.split(":")
                if "'" in res:
                    continue
                i = 0
                found = False
                while i<len(lista):
                    if res[0] is lista[i]['key']:
                        lista[i]['value'] = res[1]
                        found = True
                    i = i + 1
                if found is False:
                    lista.append({'key': res[0], 'value': res[1]})
            result = multiple_values_update(lista)

            return HttpResponse(status=200, mimetype='application/json')
        else:
            return HttpResponse(status=204, mimetype='application/json')

    else:
        return HttpResponse(status=405)

