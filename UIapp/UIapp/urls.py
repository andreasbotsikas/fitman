from django.conf.urls import patterns, include, url

from django.contrib import admin
import views
import settings

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'UIapp.views.home', name='home'),
    # url(r'^UIapp/', include('UIapp.foo.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.welcome, name='welcome'),
    url(r'^welcome$', views.welcome, name='welcome'),
    url(r'^welcome-account', views.welcome_account, name='welcome-account'),
    url(r'^welcome-train', views.welcome_train, name='welcome-train'),
    url(r'^welcome-categories', views.welcome_categories, name='welcome-categories'),
    url(r'^create_query$', views.create_query, name='create_query'),
    url(r'^dashboard$', views.home, name='home'),
    url(r'^queries/(\d+)$', views.results, name='results'),
    url(r'^welcome_account', views.welcome_account, name='welcome_account'),
    url(r'^welcome_train$', views.welcome_train, name='welcome_train'),
    url(r'^test', views.test, name='template'),
    (r'^s/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_DOC_ROOT}),
)


