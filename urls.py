from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'guest.views.home', name='home'),
    url(r'^rsvp_login$', 'guest.views.rsvp_login', name='rsvp_login'),
    url(r'^rsvp$', 'guest.views.rsvp', name='rsvp'),
)
