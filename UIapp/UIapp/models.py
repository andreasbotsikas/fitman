__author__ = 'Jo'

from django.db import models
from django.contrib.auth.models import Group

# Accounts, Keywords, Materials, Companies
class Category(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)

    class Admin:
        pass

    def __unicode__(self):
        return "%s" % self.name

# Every Group may create a series of values for the categories
class Category_value(models.Model):
    value = models.CharField(max_length=255, blank=True)
    category = models.ManyToManyField(Category, blank=False)
    created_by = models.ForeignKey(Group, blank=False)

    class Admin:
        pass

    def __unicode__(self):
        return "%s" % self.value


class Query(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    venn = models.CharField(max_length=5, default="OR", blank=False, )
    #query = models.TextField(null=True, blank=True)  # JSON query
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)


class Query_properties(models.Model):
    query = models.ForeignKey(Query, blank=False)
    value = models.ManyToManyField(Category_value, blank=False)


class Results(models.Model):
    query = models.ForeignKey(Query, blank=False)
    results = models.TextField(null=True, blank=True)  # JSON result
    updated = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)


