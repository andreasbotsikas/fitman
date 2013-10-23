__author__ = 'mpetyx'


from django.contrib import admin
from models import *

class CategoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)

class Category_valueAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category_value, Category_valueAdmin)

class QueryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Query, QueryAdmin)
