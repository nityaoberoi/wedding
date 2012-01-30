import time, logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from guest.models import Guest, COMING_OPTS
from guest.forms import GuestForm, GuestEmailForm

def home(request):
    start_rt = time.time()
    template = 'index.html'
    #rt = template.render(path, {})
    #logging.debug("LOG: Rendering main page took: %s secs" , time.time()-start_rt)
    return render(request, template, context)

def rsvp_login(request):
    context = {}
    if request.method == "POST":
        email = request.POST.get('email')
        guest, created = Guest.objects.get_or_create(email=email)
        form = GuestEmailForm(request.POST, instance=guest)
        if form.is_valid():
            guest = form.save()
            context['guest'] = guest
            context['form'] = GuestForm(instance=guest)
            context['coming_choices'] = COMING_OPTS
            if not created:
                context['disabled'] = True
            return render(request, 'rsvp2.html', context)
    else:
        form = GuestEmailForm()
    context['form'] = form
    return render(request, 'rsvp-login.html', context)
    
def rsvp(request):
    # shouldn't get here if not a post
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        logging.info(email)
        try:
            guest = Guest.objects.get(email=email)
        except Guest.DoesNotExist:
            return HttpResponseRedirect(reverse('rsvp_login'))
        form = GuestForm(request.POST, instance=guest)
        logging.info(request.POST)
        logging.info("Guest %s" % guest)
        if form.is_valid():
            message = request.POST.get('message')
            # TODO: Sriram, I'll take care of this in the evening. If you'd like to do it, and know how please go ahead though.
            #if message:
              # logging.debug("%s wrote %s" % (fullname, message))
            #  guest.message.append("@%s -- %s" % (time_str(time.time(), message)))
            guest = form.save()
            return render(request, 'thanks.html', {})
        context['form'] = form
        return render(request, 'rsvp2.html', context)
    return HttpResponseRedirect(reverse('rsvp_login'))
