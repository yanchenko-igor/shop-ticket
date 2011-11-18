from django.conf.urls.defaults import *
from localsite.feeds import EventFeed
from flatblocks.views import edit
from django.contrib.auth.decorators import login_required

from satchmo_store.urls import urlpatterns

my_urlpatterns = patterns('',
    url(r'^latest/$', EventFeed(), name='eventfeed'),
)

urlpatterns += my_urlpatterns
