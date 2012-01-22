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
  coming = db.StringProperty(required=True)

  # Hotel specific. June 9 8am until Jun 9 11:59
  checkin = db.StringProperty()  # TODO: datetime?
  checkout = db.StringProperty()
  ride_from_bom = db.BooleanProperty()

  # Other flight info, whatever they want to say
  message = db.StringProperty(multiline=True)

  """
  # If flying into Bombay airport, tell us
  landing_at_bom = db.BooleanProperty()
  arrival = db.StringProperty()
  departure = db.StringProperty()
  """

  # Private information about guests
  notes = db.StringProperty()
  updated = db.IntegerProperty()


class RSVPGuest(webapp2.RequestHandler):
  """Update RSVP info for a guest"""
  def get(self):
    fullname = self.request.get('fullname')
    email = self.request.get('email')
    coming = self.request.get('coming')
    if not fullname:
      #self.response.headers['Content-Type'] = 'text/html'
      self.redirect('/rsvp.html?rsvp_status=%s' % coming)
      return

    logging.debug("%s rsvp'ed %s" % (fullname, coming))
    guest = Guest(name=fullname, coming=coming, email=email)
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
      guest.message = message

    guest.put()  # save the guests info
    self.redirect('/confirmation.html?email=%s' % email)

class ConfirmationPage(webapp2.RequestHandler):
  def get(self):
    def time_str(timestamp):
      return time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(timestamp)
        ) if timestamp else '-'

    self.response.headers['Content-Type'] = 'text/html'
    email = self.request.get('email')
    logging.info("Checking RSVP for %s" % email)
    query = db.GqlQuery("SELECT * FROM Guest WHERE email='%s'" % email)
    rsvps = []
    for guest in query:
      status = "- %s rsvp'd %s @ %s." % (
        guest.name, guest.coming, time_str(guest.updated))

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


def date_range(date_range):
  reply = []
  for day in date_range:
    reply.append(day)

  return reply

class RSVPHTMLPage(webapp2.RequestHandler):
  def get(self):

    self.response.headers['Content-Type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')
    rsvp_status = self.request.get('rsvp_status')
    if rsvp_status not in ["yes", "no", "maybe"]:
      rsvp_status = ""

    opts = {"": "", "yes": "Yes, of course!",
            "no": "No, I'm unable to.", "maybe": "I'll decide soon"}
    rsvp_opts = map(lambda (x,y): (x,y, x==rsvp_status), opts.items())

    checkin_opts = [""] + date_range(["Fri, Jun 8 2012",
                                                 "Sat, Jun 9 2012",
                                                 "Sun, Jan 10 2012"])

    checkout_opts = [""] + date_range(["Sun, Jan 10 2011",
                                                  "Mon, Jan 11 2012"])


    self.response.out.write(template.render(path,{
          'rsvp_main_opts': rsvp_opts,
          "checkin_opts": checkin_opts,
          "checkout_opts": checkout_opts}))

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

logging.getLogger().setLevel(logging.DEBUG)
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/rsvp-guest', RSVPGuest),
                               ('/rsvp.html', RSVPHTMLPage),
                               ('/delete', DeletePage),
                               ('/confirmation.html', ConfirmationPage),])
