#!/usr/lib/python2.5

import logging, os, time, webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      rt = template.render(path, {})  # rendered template
      self.response.out.write(rt)

class Guest(db.Model):
  name = db.StringProperty(required=True)
  coming = db.BooleanProperty(required=True)
  message = db.StringProperty()
  
class RSVPConf(webapp2.RequestHandler):
  def get(self):
    fullname = self.request.get('fullname')
    if not fullname:
      self.redirect('/rsvp.html')

    coming = self.request.get('coming')
    message = self.request.get('message')
    
    g = Guest(name=fullname, coming=coming, message=message)
    g.put()
    self.response.out.write('%s: coming: %s, message: %s' % (
        fullname, coming, message))

class RSVPHTMLPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')
    self.response.out.write(template.render(path,{}))


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rsvp', RSVPConf),
                               ('/rsvp.html', RSVPHTMLPage)])
