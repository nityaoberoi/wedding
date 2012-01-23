#!/usr/lib/python2.7

import logging, os, time, webapp2
from google.appengine.ext import db
from google.appengine.ext.webapp import template

SAFETY_MODE = 1

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      start_rt = time.time()
      rt = template.render(path, {})  # rendered template
      logging.debug("LOG: Rendering main page took: %s secs" , time.time()-start_rt)
      self.response.out.write(rt)

class Guest(db.Model):
  email = db.StringProperty(required=True)
  name = db.StringProperty()
  coming = db.StringProperty()
  count = db.IntegerProperty()

  # Hotel specific. June 9 8am until Jun 9 11:59
  checkin = db.StringProperty()  # TODO: datetime?
  checkout = db.StringProperty()
  ride_from_bom = db.BooleanProperty()

  # Other flight info, whatever they want to say
  message = db.StringListProperty()
  """
  # If flying into Bombay airport, tell ur ARR/DEP details
  arrival = db.StringProperty()
  departure = db.StringProperty()
  """
  # Private information about guests
  notes = db.StringProperty()
  updated = db.IntegerProperty()

  def __str__(self):
    return "%s (%s) rsvp'd %s for a group of %d. Hotel: %s until %s." % (
      self.name, self.email, self.coming, self.count, self.checkin, self.checkout)

class RSVPLoginHTMLPage(webapp2.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'rsvp-login.html')
    self.response.out.write(template.render(path,{}))

class RSVPLogin(webapp2.RequestHandler):
  """On submitting email in RSVP Login page."""
  def get(self):
    email = self.request.get('email')
    if not email:
      self.redirect('/rsvp-login.html')
    elif lookup_user_email(email):
      # email matched in current RSVP list
      self.redirect('/confirmation.html?email=%s' % email)
    else:
      # send the user to RSVP page, with only email detail filled.
      self.redirect('/rsvp.html?email=%s' % email)

    return

class RSVPHTMLPage(webapp2.RequestHandler):
  def get(self):
    email = self.request.get("email")
    if not email:  # go thru the email workflow
      self.redirect("/rsvp-login.html")
      return

    guest = lookup_user_email(email)
    if not guest:
      guest = Guest(email=email)
      guest.put()

    logging.info("Guest: %s; coming: %s" % (guest.name, guest.coming))
    opts = {"yes": "Yes, of course!", "no": "No, I'm unable to.", 
            "maybe": "I'll decide soon"}
    rsvp_opts = map(lambda (x,y): (x,y, guest.coming==x), opts.items())

    checkin_opts = ["Sat, June 9 2012", "Sun, June 10 2012"]
    checkout_opts = ["Sun, June 10 2012", "Mon, June 11 2012"]
    count_opts = range(1,5)  # 1-4 people

    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')
    self.response.out.write(template.render(path,{
          'rsvp_main_opts': rsvp_opts, "guest": guest,
          "checkin_opts": checkin_opts, "checkout_opts": checkout_opts,
          "count_opts": count_opts}))

class RSVPSubmit(webapp2.RequestHandler):
  """On submitting the RSVP details/message."""
  def get(self):
    email = self.request.get('email')
    if not email:
      self.redirect('/rsvp-login.html')
      return

    guest = lookup_user_email(email)
    if not guest:
      logging.warn("No guest has registered yet as %s" % email)
      self.redirect('/rsvp.html?email=%s' % email)
      return

    for attr in ['name', 'email', 'coming', 'checkin', 'checkout', 
                 'ride-from-bom']:
      data = self.request.get(attr)      
      if data and data != getattr(guest, attr):
        logging.info("%s (%s) updated %s with %s (was %s)" % (
            guest.name, guest.email, attr, data, getattr(guest,attr)))
        setattr(guest, attr, data)

    # TODO: make this part of for once count is an integer
    count = self.request.get('count')
    if type(count) != int:
      try:
        count = int(count)
      except:
        count = 0
    guest.count = count

    message = self.request.get('message')
    if message:
      logging.debug("%s wrote %s" % (guest.name, message))
      guest.message.append("%s: %s" % (time_str(time.time()), message))
    guest.updated = int(time.time())
    guest.put()  # save the guests info
    self.redirect('/confirmation.html?email=%s' % email)

class ConfirmationPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    email = self.request.get('email')
    logging.info("Checking RSVP for %s" % email)
    query = db.GqlQuery("SELECT * FROM Guest WHERE email='%s'" % email)
    rsvps = []
    for guest in query:
      status = str(guest)
      logging.info(status)
      for msg in guest.message:
        logging.info(msg)
      rsvps.append(status+"\n")

    path = os.path.join(os.path.dirname(__file__), 'confirmation.html')
    self.response.out.write(template.render(path, {
          "rsvps": rsvps, "email": email,}))

class DeletePage(webapp2.RequestHandler):
  def get(self):
    if SAFETY_MODE:
      return

    logging.debug("DELETING RSVP users:")
    count = 0
    for g in Guest.all():
      logging.debug("%s said %s. Deleting" % (g.name, g.coming))
      g.delete()
      count += 1

    self.response.out.write("There are %d users" % count)

def time_str(timestamp):
  return time.strftime(
    "%Y-%m-%d %H:%M:%S", time.localtime(timestamp)
    ) if timestamp else ''

def lookup_user_email(email, all=False):
  query = db.GqlQuery("SELECT * FROM Guest WHERE email='%s'" % email)
  guest_list = []
  for guest in query:
    guest_list.append(guest)

  if all:
    return guest_list

  return guest_list[0]  if guest_list else []

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rsvp-login.html', RSVPLoginHTMLPage),
                               ('/rsvp-login', RSVPLogin),
                               ('/rsvp.html', RSVPHTMLPage),
                               ('/rsvp-submit', RSVPSubmit),
                               #('/rsvp-login', RSVPLoggedInView),
                               ('/delete', DeletePage),
                               ('/confirmation.html', ConfirmationPage),])
