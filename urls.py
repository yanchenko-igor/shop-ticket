from django.conf.urls.defaults import *
from localsite.feeds import EventFeed

from satchmo_store.urls import urlpatterns

my_urlpatterns = patterns('',
    url(r'^latest/$', EventFeed(), name='eventfeed'),
)

urlpatterns += my_urlpatterns
