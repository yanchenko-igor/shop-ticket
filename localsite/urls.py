from django.conf.urls.defaults import *
from localsite.forms import EventForm1, EventForm2, EventForm3, EventForm4
from localsite.views import EventWizard

eventforms = [EventForm1, EventForm2, EventForm3, EventForm4]

urlpatterns = patterns('',
    (r'example/', 'store.localsite.views.example', {}),
    (r'^event/$', EventWizard.as_view(eventforms)),
)
