#!/usr/lib/python2.7

import logging, os, time, webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      start_rt = time.time()
      rt = template.render(path, {})  # rendered template
      logging.debug("LOG: Rendering main page took: %s secs" , time.time()-start_rt)
      self.response.out.write(rt)

class Guest(db.Model):
  name = db.StringProperty(required=True)
  coming = db.StringProperty(required=True)
  message = db.StringProperty()

class RSVPConf(webapp2.RequestHandler):
  def get(self):
    fullname = self.request.get('fullname')
    if not fullname:
      self.redirect('/rsvp.html')

    coming = self.request.get('coming')
    message = self.request.get('message')
    logging.debug("%s rsvp'ed %s" % (fullname, coming))
    Guest(name=fullname, coming=coming, message=message).put()
    self.response.out.write('%s: coming: %s, message: %s' % (
        fullname, coming, message))

class RSVPConfCheck(webapp2.RequestHandler):
  def get(self):
    fullname = self.request.get('name')
    logging.debug("Checking RSVP for %s" % fullname)
    query = Guest.gql("WHERE name='%s'" % fullname)
    for name in query:
      logging.debug("%s:" % name.__dict__)


class RSVPHTMLPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')
    self.response.out.write(template.render(path,{}))

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rsvp', RSVPConf),
                               ('/rsvp-check', RSVPConfCheck),
                               ('/rsvp.html', RSVPHTMLPage)])
