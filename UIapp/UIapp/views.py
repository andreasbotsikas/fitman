__author__ = 'Jo'

import urllib2,urllib
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
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from initialiaze_repo import initialize
from models import Category, Team, Project, Category_value, Query, Query_properties, Results,Query_languages
from updateSentimentKeys import multiple_values_update
import csv
import configurations
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
#from django.shortcuts import resolve_url
from django.core.urlresolvers import reverse, resolve
from django.template.response import TemplateResponse
from django.contrib.auth.views import password_reset


def index(request):
    return render_to_response("index.html")


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/welcome")

def contact(request):
    return render_to_response("contact.html")

def about(request):
    return render_to_response("about.html")

def welcome(request):
    if request.user.is_authenticated():
        # Do something for authenticated users.
        #print ('is autenticated')
        return HttpResponseRedirect("/dashboard") # Redirect after POST

    if request.method == 'POST': # If the form has been submitted...
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user = authenticate(username=email, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                login(request, user)
                print("User is valid, active and authenticated")
                #set user on session property to read it from results
            else:
                print("The password is valid, but the account has been disabled!")
                return HttpResponseRedirect("/") # Redirect after POST
        else:
            # the authentication system was unable to verify the username and password
            #print("The username or password were incorrect.")
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
        username=request.POST.get("username","")
        email=request.POST.get("email","")
        password=request.POST.get("password","")
        password2=request.POST.get("password2","")
        if str(username).isspace() or str(email).isspace() or str(password).isspace(): #strings with gaps
            return render(request, "signup.html", {"message": 'Please fill in all the fields'})
        elif not str(username) or not str(email) or not str(password) or not str(password2): #empty strings
            return render(request, "signup.html", {"message": 'Please fill in all the fields'})
        elif User.objects.filter(username=(str(username).lower())): #user exists
            return render(request, "signup.html", {"message": 'Choose another username'})
        elif User.objects.filter(username=(str(email).lower())): # email exists
            return render(request, "signup.html", {"message": 'This email is in use'})
        elif str(password)!= str(password2): #not same password
            return render(request, "signup.html", {"message": 'Wrong password verification'})
        else:
            request.session['signup-username']=str(username).lower()
            request.session['signup-email']=str(email).lower()
            request.session['signup-password'] = password

        return HttpResponseRedirect("/welcome-categories")
    else:
        return render(request, 'signup.html')

def welcome_account(request):
    if request.method == 'POST': # If the form has been submitted...
        email=request.POST.get("email","")
        password=request.POST.get("password","")
        user = authenticate(username=email, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                print("User is valid, active and authenticated")
                #set user on session property to read it from results
            else:
                #print("The password is valid, but the account has been disabled!")
                return HttpResponseRedirect("/") # Redirect after POST
        else:
            # the authentication system was unable to verify the username and password
            #print("The username or password were incorrect.")
            return HttpResponseRedirect("/") # Redirect after POST

        #Check authenticated
        #If  ok
        return HttpResponseRedirect("/dashboard") # Redirect after POST
        #If not authenticated
        #inform
    else:
        #for development mode only!!
        #initialize()
        return render(request, "welcome.html")

    return render_to_response("welcome_account.html")



## step1
def welcome_categories(request):
    #must create project!
    if request.method == 'POST': # If the form has been submitted...
        #from session
        email = request.session.get("signup-email")
        password = request.session.get("signup-password")
        username=request.session.get("signup-username")
        #from request parameters
        project=request.POST.get("project","")
        twitter=request.POST.get("twitter","")
        facebook=request.POST.get("facebook","")
        hashtags=request.POST.get("hashtags","")
        rss=request.POST.get("rss","")

        twitter_properties=""
        facebook_properties=""

        if str(project).isspace() or not str(project): #not a project name
            return render(request, "welcome_categories.html", {"message": 'Project name is required' })
        elif str(project).isspace() or str(twitter).isspace() or str(facebook).isspace() or str(hashtags).isspace() or str(hashtags).isspace(): #strings with gaps
            return render(request, "welcome_categories.html", {"message": 'Please remove empty spaces' })
        elif not str(twitter) and not str(facebook) and not str(hashtags) and not str(rss): #empty strings
            return render(request, "welcome_categories.html", {"message": 'Please provide at least one parameter to initialize your project'})
        else:
            #create user
            #create project
            #create properties
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
            #print user
            team = Team(name=username, created_by=user)
            team.save()
            project = Project(name=project, created_by=user, owned_by=team)
            project.save()
            categoryK = Category.objects.get(name="Keywords")
            categoryT = Category.objects.get(name="Twitter")
            categoryF = Category.objects.get(name="Facebook")
            categoryR = Category.objects.get(name="RSS")
            if twitter:
                Category_value.objects.create(value=twitter, category=categoryT, owned_by=project).save()
                twitter_properties+=twitter
            else:
                Category_value.objects.create(value="", category=categoryT, owned_by=project).save()
            if facebook:
                Category_value.objects.create(value=facebook, category=categoryF, owned_by=project).save()
                facebook_properties+=facebook
            else:
                Category_value.objects.create(value="", category=categoryF, owned_by=project).save()
            if hashtags:
                Category_value.objects.create(value=hashtags, category=categoryK, owned_by=project).save()
                twitter_properties += ",%s" %hashtags
            else:
                Category_value.objects.create(value="", category=categoryK, owned_by=project).save()
            if rss:
                Category_value.objects.create(value=rss, category=categoryR, owned_by=project).save()
            else:
                Category_value.objects.create(value="", category=categoryR, owned_by=project).save()
            user2 = authenticate(username=username, password=password)
            if user2 is not None:
                # the password verified for the user
                if user2.is_active:
                    login(request, user2)
                    print("User is valid, active and authenticated")
                    #set user on session property to read it from results
                else:
                    print("The password is valid, but the account has been disabled!")
                    return HttpResponseRedirect("/") # Redirect after POST
            else:
                # the authentication system was unable to verify the username and password
                #print("The username or password were incorrect.")
                return HttpResponseRedirect("/signup") # Redirect after POST


        request.session['signup-username']=""
        request.session['signup-email']=""
        request.session['signup-password']=""

        # setup project on twitter connector
        update_twitter_connector(username, project, twitter_properties)
        # setup project on fb connector
        update_facebook_connector(username, project, facebook_properties)
        # setup project on RSS GE

        return HttpResponseRedirect("/welcome-train")
    else:

        return render(request, 'welcome_categories.html')

## step 2
def welcome_train(request):
    #we have now user, thus we must authenticate them before train the system to avoid attacks
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/") # Redirect to initial screen

    if request.method == 'POST': # If the form has been submitted...
        #must handle .csv
        csv=request.FILES.get("file","")
        file = request.FILES['file']
        if file.content_type == 'text/csv':
            req = urllib2.Request(configurations.sentiment_training_path)
            req.add_header('-T',file)
            resp = urllib2.urlopen(req)
            response = resp.read()
            return HttpResponseRedirect("/welcome-report") # Redirect after POST
        else:
            #print "not valid file"
            return HttpResponseRedirect("/welcome-train") #

    else:
        return render(request,'welcome_train.html')

## step 3
def welcome_report(request):
    #we have now user, thus we must authenticate them before train the system to avoid attacks
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/") # Redirect to initial screen
    if request.method == 'POST':
        run_query (request)
        return HttpResponseRedirect("/dashboard") # Redirect after POST

    return render(request, "welcome_report.html")

def settings(request):
    if request.user.is_authenticated():
        project=Project.objects.filter(created_by=request.user).latest("created")
        if request.method != 'POST':
            keywords=twitter=facebook=rss=""
            for project_settings in Category_value.objects.filter(owned_by=project):
                if project_settings.category.name=="Keywords":
                    keywords = project_settings.value
                elif project_settings.category.name=="Twitter":
                    twitter = project_settings.value
                elif project_settings.category.name=="Facebook":
                    facebook = project_settings.value
                elif project_settings.category.name=="RSS":
                    rss = project_settings.value

            return render(request, "settings.html",{"keywords":keywords,"twitter":twitter, "facebook":facebook, "rss":rss})
        else:
            #get properties
            twitter = request.POST.get("twitter","")
            facebook = request.POST.get("facebook","")
            keywords = request.POST.get("keywords","")
            rss = request.POST.get("rss","")
            #update twitter
            category = Category.objects.get(name="Twitter")
            if Category_value.objects.filter(owned_by=project, category=category).count()==0:
                Category_value.objects.create(owned_by=project, category=category, value="").save()
            else:
                category_val=Category_value.objects.get(owned_by=project, category=category)
            category_val.value=twitter
            category_val.save()

            #update facebook
            category = Category.objects.get(name="Facebook")
            if Category_value.objects.filter(owned_by=project, category=category).count()==0:
                Category_value.objects.create(owned_by=project, category=category, value="").save()
            else:
                category_val=Category_value.objects.get(owned_by=project, category=category)
            category_val.value=facebook
            category_val.save()

            #update keywords
            category = Category.objects.get(name="Keywords")
            if Category_value.objects.filter(owned_by=project, category=category).count()==0:
                Category_value.objects.create(owned_by=project, category=category, value="").save()
            else:
                category_val=Category_value.objects.get(owned_by=project, category=category)
            category_val.value=keywords
            category_val.save()

            #update rss
            category = Category.objects.get(name="RSS")
            if Category_value.objects.filter(owned_by=project, category=category).count()==0:
                Category_value.objects.create(owned_by=project, category=category, value="").save()
            else:
                category_val=Category_value.objects.get(owned_by=project, category=category)
            category_val.value=rss
            category_val.save()

            twitter_properties=twitter+','+keywords
            #update twitter connector
            update_twitter_connector(project.owned_by.name, project.name, twitter_properties)
            #update facebook connector
            update_facebook_connector(project.owned_by.name, project.name, facebook)
            #update RSS connector

            return render(request, "settings.html",{"keywords":keywords,"twitter":twitter, "facebook":facebook, "rss":rss})
    else:
        return HttpResponseRedirect("/")

def create_query(request):
    if not request.user.is_authenticated():
        # Do something for anonymous users.
        return HttpResponseRedirect("/dashboard") # Redirect after POST

    if request.method == 'POST': # If the form has been submitted...
        ##Do not allow users to vote before a timeperiod has passed.
        run_query (request)

        return HttpResponseRedirect("/dashboard") # Redirect after POST
    else:
        return render(request, 'create_query.html')


def home(request):
    # get the authenicated user instead
    #teams = Team.objects.filter(created_by=request.user)
    # # to be selected by the user
    # current_team=teams.latest()
    # projects=Project.objects.filter(owned_by=current_team.name, created_by=user.username)

    if request.user.is_authenticated():
        current_project=Project.objects.filter(created_by=request.user).latest("created")
        queries = Query.objects.filter(owned_by=current_project.id)
        list_of_queries = []
        titles = ['Name', 'Keywords', 'Accounts', 'Created by', 'From', 'To', 'Created']
        for query in queries:
            query_response = {}
            query_response['id'] = query.id
            query_response['Name'] = query.name
            query_response['Created_by'] = query.created_by.username
            query_response['From'] = query.from_date.date()
            query_response['To'] = query.to_date.date()
            query_response['Created'] = query.created.date()

            #query_response= "{'id':'%s','Name': '%s'" %(query.id, query.name)
            dynamic_properties = get_query_properties(query)["Properties"]
            if (dynamic_properties.get("Keywords")or dynamic_properties.get("keywords")):
                query_response['Keywords'] = dynamic_properties["Keywords"]
            if (dynamic_properties.get("Twitter")or dynamic_properties.get("twitter")):
                query_response['Usernames'] = dynamic_properties["Twitter"]
            if (dynamic_properties.get("Facebook") or dynamic_properties.get("facebook")):
                query_response['Usernames'] = dynamic_properties["Facebook"]
            ##print "The property name is:%s" % query_response['Keywords']

            # query_properties = Query_properties.objects.filter(query=query)
            # for query_property in query_properties:
            #     #print "The property object is:%s" %query_property.category.name
            #     # a Category that must a appear in the table header
            #     #if query_property.category.name not in titles:
            #         #titles.append("%s" % query_property.category.name)
            #     # add the property name & value to the response
            #     if query_property.category.name=='Keywords':
            #         #query_response += ",'%s':%s"%(query_property.category.name, query_property.properties)
            #         query_response['Keywords']=query_property.properties
            #         #print "The property name is:%s" %query_property.properties
            list_of_queries.append(query_response)
        return render_to_response("home.html", {"headers": titles, "content": list_of_queries})
    else:
        return HttpResponseRedirect("/")


def analytics(request):
    return render_to_response("analytics.html")

# create a query
def run_query (request):
    user = request.user
    project = Project.objects.get(created_by=user)
    query_name = request.POST.get("query_name", "")
    from_date = request.POST.get("datepicker_from", "")
    to_date = request.POST.get("datepicker_to", "")
    language = request.POST.get("lan", "")
    query = Query(name=query_name, venn="", from_date=parser.parse(from_date), to_date=parser.parse(to_date),
                  created=timezone.now(), created_by=user, owned_by=project)
    query.save()
    keywords = request.POST.get("keywords", "")
    category = Category.objects.get(name="Keywords")
    query_property = Query_properties(query=query, category=category, properties=keywords)
    query_property.save()
    twitter = request.POST.get("twitter", "")
    category = Category.objects.get(name="Twitter")
    query_property = Query_properties(query=query, category=category, properties=twitter)
    query_property.save()
    brands = request.POST.get("brands", "")
    try:
        category = Category.objects.filter(name="brands")
    except ValueError:
        print ValueError.message
    if category.__len__(): #exists already the category
        category = category[0]
    ## otherwise create the category
    else:
        #print "is empty"
        category = Category(name="brands")
        category.save()
    query_property = Query_properties(query=query, category=category, properties=brands)
    query_property.save()
    query_lan=Query_languages(query=query,language=language)
    query_lan.save()

    ##handle dynamic properties
    i = 0;
    prop_value = "prop-value-%s" % i
    prop_name = "prop-name-%s" % i
    while request.POST.get(prop_value, ""):
        property_name = request.POST.get(prop_name, "")
        property_value = request.POST.get(prop_value, "")
        try:
            ## try to find if the category already exists - in lowercase
            category = Category.objects.filter(name=(str(property_name).lower()))
        except ValueError:
            #print ValueError.message
            continue

        if category.__len__(): #exists already the category
            category = category[0]
        ## otherwise create the category
        else:
            category = Category(name=str(property_name).lower())
            category.save()
            ## end store the properties in the category
        query_property = Query_properties(query=query, category=category, properties=property_value)
        query_property.save()

        i += 1
        prop_value = "prop-value-%s" % i
        prop_name = "prop-name-%s" % i

    return query.id



def results(request, query_id):
    #if authorized
    #MUST DEVELOP
    """
    :param request:
    :param query_id:
    :return: :raise:
    """
    if request.user.is_authenticated():
        data = []
        test =[]
        categories_counter = []
        positive_counter = 0
        negative_counter = 0
        neutral_counter = 0
        try:
            #query_id = str(query_id)
            ## Must store the response, if there is no response, otherwise return the stored one.
            ## IF NOT STORED
            query = Query.objects.get(id=query_id,created_by=request.user)
            query_params=Query_properties.objects.filter(query=query)
            results = Results.objects.filter(query=query)
            #run for all categories
            list_properties = get_query_properties(query)
            properties=list_properties["Properties"]
            #print "properties: %s" %properties
            phrases=list_properties["Phrases"]
            #print "phrases: %s" %phrases
            keywords=list_properties["Keywords"]
            #print "keywords: %s" %keywords
            query_properties = '' # This is the string that forms the properties query (query_string)
            phrase_properties = '' # This is the string that forms the phrase query (match_phrase)'

            ## Run the query or bring the results from the Database
            if results: #bring it from the database
                response = results.__getitem__(0).results
                response = json.loads(response)
            else: #make a new query
                lang=Query_languages.objects.get(query=query_id)

                for kwrd in keywords.keys():
                    temp=''
                    for keyword_prop in keywords[kwrd]:
                        temp += "%s," %keyword_prop
                    temp=remove_comma_at_the_end(temp)
                    query_properties += '+(%s)' % temp

                if len(properties)==0: #empty list, no properties, query all
                    query_properties= '*'

                if query_properties=="+()": #if all properties are phrases, remove this field
                    query_properties=''
                else:
                    if lang:
                            if lang.language=="es":
                                query_properties='{"query_string":{"query":"%s","fields":["%s"]}}' %(query_properties,"text_no_url_es")
                            elif lang.language=="en":
                                query_properties='{"query_string":{"query":"%s","fields":["%s"]}}' %(query_properties,"text_no_url")
                            else:
                                query_properties='{"query_string":{"query":"%s","fields":["%s","%s"]}}' %(query_properties,"text_no_url","text_no_url_es")
                    else:
                        query_properties='{"query_string":{"query":"%s","fields":["%s"]}}' %(query_properties,"text_no_url")

                # Create the phrase query
                for phrase_list in phrases.keys():
                    for phrase in phrases[phrase_list]:
                        if lang:
                            if lang.language=="es":
                                phrase_properties+='{"match_phrase":{"doc.text_no_url_es":"%s"}},'%phrase

                            elif lang.language=="en":
                                phrase_properties+='{"match_phrase":{"doc.text_no_url":"%s"}},'%phrase
                            else:
                                phrase_properties+='{"match_phrase":{"doc.text_no_url":"%s"}},{"match_phrase":{"doc.text_no_url_es":"%s"}},'%(phrase,phrase)
                        else:
                            phrase_properties+='{"match_phrase":{"doc.text_no_url":"%s"}},'%phrase

                phrase_properties=remove_comma_at_the_end(phrase_properties)
                if (query_properties!='') and (phrase_properties!=''):
                    query_all = '{"query":{"filtered":{"query":{"bool":{"should":[%s,%s],"minimum_should_match" : 1}},"filter":{"bool":{"must":[{"range":{"doc.created_at":{"from":"%s","to":"%s"}}}],"_cache":true}}}},"from":0,"size":100000, "sort":["_score"]}' % (
                                query_properties,
                                phrase_properties,
                                int(time.mktime(query.from_date.timetuple()) * 1000),
                                int(time.mktime(query.to_date.timetuple()) * 1000))
                else:
                    query_all = '{"query":{"filtered":{"query":{"bool":{"should":[%s %s],"minimum_should_match" : 1}},"filter":{"bool":{"must":[{"range":{"doc.created_at":{"from":"%s","to":"%s"}}}],"_cache":true}}}},"from":0,"size":100000, "sort":["_score"]}' % (
                                query_properties,
                                phrase_properties,
                                int(time.mktime(query.from_date.timetuple()) * 1000),
                                int(time.mktime(query.to_date.timetuple()) * 1000))


                #print query_all
                response = parse_query_for_sentiments(query_all)
                newResponse = Results(query=query, results=json.dumps(response), updated=datetime.datetime.now())
                newResponse.save()


            ## count the occurrences in response
            for property in properties.keys():
                list = properties[property].split(",")
                word_counter = []
                for phrase in list:
                    number = json.dumps(response).count(phrase)
                    text = '{"name":"%s","times":"%s", "sentiment":0}' % (phrase, number)
                    word_counter.append(json.loads(text))
                text = {}
                text["category"] = property
                text["properties"] = word_counter
                categories_counter.append(text)
            for message in response:
                #if message["_score"] > 0.05:
                    test.append(message["_source"])
                    data.append(message["_source"]["doc"])
                    ##print "Just Added: %s" %message["_source"]["doc"]
                    try:
                        if message["_source"]["doc"]["senti_tag"] == "positive":
                            # for global metrics
                            positive_counter += 1
                            # for mosaic diagram
                            for category in categories_counter:
                                for property in category["properties"]:
                                    if (json.dumps(message["_source"]["doc"]["text"])).find(property["name"]) > 0:
                                        #print " Message with positive tag: %s : the found property is: %s"%(json.dumps(message["_source"]["doc"]), property["name"])
                                        pos_number = int(property["sentiment"]) + 1
                                        property["sentiment"] = pos_number

                        elif message["_source"]["doc"]["senti_tag"] == "negative":
                            negative_counter += 1
                            #print "Found a message with negative tag: %s " % json.dumps(message["_source"]["doc"])
                            # for mosaic diagram
                            for category in categories_counter:
                                for property in category:
                                    if (json.dumps(message["_source"]["doc"]["text"])).find(property["name"]) > 0:
                                        neg_number = int(property["sentiment"]) - 1
                                        property["sentiment"] = neg_number

                        elif message["_source"]["doc"]["senti_tag"] == "neutral":
                            neutral_counter += 1
                    except:
                        continue
        except ValueError:
            #print ValueError.message
            raise Http404()

        return render(request, "results.html",
                      {"query_id": query.id, "query_name": query.name, "query":query_params , "response": test, "positive": positive_counter,
                       "negative": negative_counter, "neutral": neutral_counter,
                       "categories": categories_counter})
    else:
        return HttpResponseRedirect("/")

def results_update(request):
    if request.method != 'POST': # If the form has not been submitted...
        raise Http404('Only POST methods allowed')
    update_bulk = request.POST.get("retrain", "")
    ## send the bulk to the db service
    req = urllib2.Request("http://83.212.114.237:8000/user_based_sentiment?sentiment_values=%s" % str(update_bulk))
    resp = urllib2.urlopen(req)
    # response = resp.read()
    #print "stored: %s" %response
    ## delete cashing from results, to get the updated ones from "results" methods
    results_id = request.POST.get("results-id", "")
    # query = Query.objects.get(id=results_id)
    # results = Results.objects.get(query=query)
    # if results:
    #     results.delete()
    ## redirect to the proper page again
    path = "/queries/%s" % results_id
    return HttpResponseRedirect(path) # Redirect after update to the page


def results_delete(request, query_id):
    query = Query.objects.get(id=query_id)
    query.delete()
    return HttpResponseRedirect("/dashboard") # Redirect after update to the page


def search(request):
    return render_to_response("free-search.html", {"kibana": configurations.kibana_path})


def train(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/dashboard") # Redirect after POST
    if request.method == 'POST': # If the form has been submitted...
        #must handle .csv
        lan=request.POST.get("lan","")
        csv=request.FILES.get("file","")
        file = request.FILES['file']
        if lan=="es":
            train_path=configurations.sentiment_training_path+"_es"
        else:
            train_path=configurations.sentiment_training_path
        if file.content_type == 'text/csv':
            req = urllib2.Request(train_path)
            req.add_header('-T',file)
            resp = urllib2.urlopen(req)
            response = resp.read()
            return HttpResponseRedirect("/dashboard") # Redirect after POST
        else:
            #print "not valid file"
            return HttpResponseRedirect("/training") #

    else:
        return render(request,'training.html')

# Get all the properties for a query
def get_query_properties(query):
    query_properties = Query_properties.objects.filter(query=query)
    keywords={}
    phrases={}
    properties = {}
    result={}
    #usernames = ' '
    for query_property in query_properties:
            if str(query_property.properties) is "":
                continue
            else:
                phrases[str(query_property.category.name)]=[]
                properties[str(query_property.category.name)] = str(query_property.properties)
                param_list=str(query_property.properties).split(',')
                temp=[]
                for param in param_list:
                    temp.append(param)

                for param in temp:
                    words=param.split()
                    if words.__len__()>1:
                        phrases[str(query_property.category.name)].append(param)
                        param_list.remove(param)

                keywords[str(query_property.category.name)]=param_list
    result["Properties"]=properties
    #have keywords per properties category, without phrases
    result["Keywords"]=keywords
    #have phrases per properties category
    result["Phrases"]=phrases
    return result


def parse_query_for_sentiments(query):
    response = urllib2.urlopen(
        configurations.elastic_search_path,
        query
    )
    response = response.read()
    response = json.loads(response)["hits"]["hits"]
    return response


def user_based_sentiment(request):
    if request.method == 'GET':
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

            #print lista
            result = multiple_values_update(lista)

            return HttpResponse(status=200, mimetype='application/json')
        else:
            return HttpResponse(status=204, mimetype='application/json')

    else:
        return HttpResponse(status=405)

def download_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    lan = request.GET.get("lan", "")
    #print lan
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="train-sentiment.csv"'
    writer = csv.writer(response)
    if lan=="en":
        training_query = '{"query" : {"filtered" : {"query" : {"bool" : {"should" : [{"query_string" : {"query" : "*"}}]}},"filter" : {"bool" : {"must" : [{"match_all" : {}},{"terms" : {"_type" : ["couchbaseDocument"]}},{"terms" : {"doc.lang" : ["en"]}},{"bool" : {"must" : [{"match_all" : {}}]}}]}}}},"size" : 1000,"sort": [{"doc.created_at": {"order": "desc"}}],"fields" : ["doc.text_no_url","doc.senti_tag"]}'
    else:
        training_query = '{"query" : {"filtered" : {"query" : {"bool" : {"should" : [{"query_string" : {"query" : "*"}}]}},"filter" : {"bool" : {"must" : [{"match_all" : {}},{"terms" : {"_type" : ["couchbaseDocument"]}},{"terms" : {"doc.lang" : ["es"]}},{"bool" : {"must" : [{"match_all" : {}}]}}]}}}},"size" : 1000,"sort": [{"doc.created_at": {"order": "desc"}}],"fields" : ["doc.text_no_url_es","doc.senti_tag"]}'
    parsed = parse_query_for_sentiments(training_query)
    #print parsed
    for message in parsed:
        try:
            if lan=="en":
                writer.writerow([str(message["fields"]["doc.text_no_url"]).replace(",", " ").strip(), message["fields"]["doc.senti_tag"] ])
            else:
                writer.writerow([str(message["fields"]["doc.text_no_url_es"]).replace(",", " ").strip(), message["fields"]["doc.senti_tag"] ])
        except:
            continue
    return response

def update_twitter_connector(username, project, twitter_properties):
    twitter_properties='storeKeywords?id=%s_%s&keywords=%s'%(urllib.quote(str(username)),urllib.quote(str(project)), urllib.quote(twitter_properties))
    #print twitter_properties
    path="%s%s" %(configurations.twitter_connector,twitter_properties)
    response = urllib2.urlopen(path)
    #response = response.read()
    #print response
    return 1

def update_facebook_connector(username, project, facebook_properties):
    facebook_properties='storeFBaccounts?id=%s_%s&keywords=%s'%(urllib.quote(str(username)),urllib.quote(str(project)), urllib.quote(facebook_properties))
    #print facebook_properties
    path="%s%s" %(configurations.facebook_connector,facebook_properties)
    response = urllib2.urlopen(path)
    return 1

def remove_comma_at_the_end (expression):
    if len(expression) > 0:
        if expression[-1:] == ",":
            expression = expression[:-1]
    return expression

def remove_plus_in_the_beginning (expression):
    if len(expression) > 0:
        if expression[:1] == "+":
            expression = expression[1:]
    return expression
