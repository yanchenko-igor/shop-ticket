from django.conf.urls.defaults import *

from satchmo_store.urls import urlpatterns as satchmourls

urlpatterns = patterns('', 
        url(r'^wizards/', include('localsite.urls')),
        )

urlpatterns += satchmourls
