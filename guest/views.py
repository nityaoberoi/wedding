import time, logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from guest.models import Guest, COMING_OPTS
from guest.forms import GuestForm, GuestEmailForm

def home(request):
    return render(request, 'index.html')

def rsvp_login(request):
    context = {}
    #email = request.session.get('email')
    if request.method == "POST":
        email = request.POST.get('email')
        request.session['email'] = email
        guest, created = Guest.objects.get_or_create(email=email)
        form = GuestEmailForm(request.POST, instance=guest)
        if form.is_valid():
            guest = form.save()
            context['guest'] = guest
            context['form'] = GuestForm(instance=guest)
            if not created:
                context['disabled'] = True
            return render(request, 'rsvp2.html', context)
    # elif email:
    #        try:
    #            guest = Guest.objects.get(email=email)
    #            context['guest'] = guest
    #            context['form'] = GuestForm(instance=guest)
    #            context['disabled'] = True
    #            return render(request, 'rsvp2.html', context)
    #        except Guest.DoesNotExist:
    #            form = GuestEmailForm()
    else:
        form = GuestEmailForm()
    context['form'] = form
    return render(request, 'rsvp-login.html', context)
    
def rsvp(request):
    # shouldn't get here if not a post
    context = {}
    if request.method == 'POST':
        email = request.session.get('email')
        try:
            guest = Guest.objects.get(email=email)
        except Guest.DoesNotExist:
            return HttpResponseRedirect(reverse('rsvp_login'))
        form = GuestForm(request.POST, instance=guest)
        logging.info("Guest %s" % guest)
        logging.info(request.POST)
        if form.is_valid():
            message = request.POST.get('message')
            prev_messages = guest.message or ''
            if message:
                logging.debug("%s wrote %s" % (guest.name or email, message))
                prev_messages = prev_messages + "%s: %s\n" % (time_str(time.time()), message)
            guest = form.save(commit=False)
            guest.message = prev_messages
            guest.save()            
            context['disabled'] = True
            context['thanks'] = True
            request.session['email'] = guest.email
        context['guest'] = guest
        context['form'] = form
        return render(request, 'rsvp2.html', context)
    return HttpResponseRedirect(reverse('rsvp_login'))

def time_str(timestamp):
  return time.strftime("On %b %d, %Y at %I:%M %p", time.localtime(timestamp)) if timestamp else ''