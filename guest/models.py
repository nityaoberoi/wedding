from django.db import models
from google.appengine.ext import db

COMING_OPTS = ((0, 'No'), (1, 'Yes'), (2, 'Maybe'))

class Guest(models.Model):
    email = models.EmailField(null=False, unique=True)
    name = models.CharField(max_length=50)
    coming = models.PositiveIntegerField(default=0, choices=COMING_OPTS)
    count = models.PositiveIntegerField(default=0)
    checkin = models.DateTimeField(blank=True, null=True)
    checkout = models.DateTimeField(blank=True, null=True)
    ride_from_bom = models.BooleanField(default=False)
    
    """
      # If flying into Bombay airport, tell ur ARR/DEP details
      arrival = db.StringProperty()
      departure = db.StringProperty()
    """
    
    message = models.TextField(null=True)
    updated = models.PositiveIntegerField(null=True)  ## Private information about guests

    def __str__(self):
        return "%s (%s) rsvp'd %s for a group of %d. Hotel: %s until %s." % (
      self.name, self.email, self.coming, self.count or 0, self.checkin, self.checkout)