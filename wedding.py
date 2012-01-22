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
  name = db.StringProperty(required=True)
  email = db.StringProperty(required=True)
  count = db.IntegerProperty(required=True)

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

    name = self.request.get("name")
    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')

    coming = self.request.get('coming')
    # RSVP overall choice
    opts = {"": "", "yes": "Yes, of course!",
            "no": "No, I'm unable to.", "maybe": "I'll decide soon"}
    rsvp_opts = map(lambda (x,y): (x,y, x==coming), opts.items())
    
    # Guest count for this RSVP
    count = self.request.get('count')
    logging.debug("Count is %s" % count)
    if count is None:
      pass
    elif count.isdigit():
      count = int(count)
    else:
      count = 0

    checkin = self.request.get('checkin')
    checkin_opts = ["Sat, June 9 2012", "Sun, June 10 2012"]

    checkout = self.request.get('checkout')
    checkout_opts = ["Sun, June 10 2011", "Mon, June 11 2012"]

    self.response.out.write(template.render(path,{
          'rsvp_main_opts': rsvp_opts, "email": email,
          "checkin_opts": checkin_opts, "checkout_opts": checkout_opts,
          "checkin": checkin, "checkout": checkout,}))

class RSVPSubmit(webapp2.RequestHandler):
  """On submitting the RSVP details/message."""
  def get(self):
    # TODO: pass emails along?
    fullname = self.request.get('fullname')
    email = self.request.get('email')
    coming = self.request.get('coming')
    count = int(self.request.get('count'))

    logging.debug("%s rsvp'ed %s" % (fullname, coming))
    guest = Guest(name=fullname, coming=coming, email=email, count=count)
    guest.updated = int(time.time())
    guest.put()

    attr = {}
    for x in ['checkin', 'checkout', 'ride-from-bom']:
      data = self.request.get(x)
      if data: setattr(guest, x, data)

    # TODO: make this a list of messages
    message = self.request.get('message')
    if message:
      logging.debug("%s wrote %s" % (fullname, message))
      guest.message.append(message+"\n@%s" % time_str(time.time()))

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
      status = "- %s rsvp'd %s @ %s." % (
        guest.name, "yes" if guest.count else "no", time_str(guest.updated))

      for a in ["checkin", "checkout", "ride_from_bom", "message"]:
        val = getattr(guest, a)
        if val:
          logging.debug(" %s=%s;" % (a, val))
          status += " %s=%s;" % (a, val)

      logging.info(status)
      rsvps.append(status+"\n")

    path = os.path.join(os.path.dirname(__file__), 'confirmation.html')
    self.response.out.write(template.render(path, {
          "rsvps": rsvps, "email": email,}))

class DeletePage(webapp2.RequestHandler):
  def get(self):
    if SAFETY_MODE:
      return

    logging.debug("DELETING RSVP'ed users:")
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

def lookup_user_email(email):
  query = db.GqlQuery("SELECT * FROM Guest WHERE email='%s'" % email)
  guest_list = []
  for guest in query:
    guest_list.append(guest)

  return guest_list

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rsvp-login.html', RSVPLoginHTMLPage),
                               ('/rsvp-login', RSVPLogin),
                               ('/rsvp.html', RSVPHTMLPage),
                               ('/rsvp-submit', RSVPSubmit),
                               #('/rsvp-login', RSVPLoggedInView),
                               ('/delete', DeletePage),
                               ('/confirmation.html', ConfirmationPage),])
