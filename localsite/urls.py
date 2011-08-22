from django.conf.urls.defaults import *
from localsite.forms import *
from localsite.views import EventWizard

eventforms = [ProductForm,EventFormInline]

urlpatterns = patterns('',
    (r'example/', 'store.localsite.views.example', {}),
    (r'^event/$', EventWizard.as_view(eventforms)),
)
