fitman
======

fitman implementation regarding social service enabler



Guidelines

Useful reference https://devcenter.heroku.com/articles/django

Steps

cd fitman
python manage.py runserver #site works


CREATING CUSTOM BUILDPACK for geodjango
heroku config:set BUILDPACK_URL=https://github.com/cirlabs/heroku-buildpack-geodjango

heroku config:set BUILDPACK_URL=https://github.com/mpetyx/heroku-buildpack-couchbase-geo-django