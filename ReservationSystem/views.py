from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def redirect_to_reservations(request):
    return HttpResponseRedirect(reverse('reservations:index'))