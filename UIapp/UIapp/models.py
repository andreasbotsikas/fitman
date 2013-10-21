__author__ = 'Jo'

from django.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings

# Accounts, Keywords, Materials, Companies
class Category(models.Model):
    name = models.CharField(max_length=255, blank=False, unique=True)

# Every Group may create a series of values for the categories
class Category_value(models.Model):
    value = models.CharField(max_length=255, blank=True)
    category = models.ManyToManyField(Category, blank=False)
    created_by = models.ForeignKey(Group,blank=False)

class Query(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    query = models.TextField(null=True, blank=True)  # JSON query
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)


