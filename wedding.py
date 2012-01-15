#!/usr/lib/python2.5
import logging, os, time, webapp2
from google.appengine.ext.webapp import template

class MainPage(webapp2.RequestHandler):
  def get(self):
      self.response.headers['Content-Type'] = 'text/html'
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      
      start_rt = time.time()
      rt = template.render(path, {})  # rendered template
      logging.info("LOG: Rendering main page took: %s secs" , time.time()-start_rt)
      print "P: Rendering main page took: %s secs" , time.time()-start_rt)
      sys.stdout.write("Rendering main page took: %s secs" , time.time()-start_rt))
      self.response.out.write(rt)

class RSVPPage(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html'
    path = os.path.join(os.path.dirname(__file__), 'rsvp.html')
    self.response.out.write(template.render(path,{}))


def main(argv):
  logging.getLogger().setLevel(logging.DEBUG)
  app = webapp2.WSGIApplication([('/', MainPage),
                                 ('/rsvp', RSVPPage)],
                                debug=True)
  
  sys.stdout.write("FUCK")


if __name__ == '__main__':
  main(sys.argv)
