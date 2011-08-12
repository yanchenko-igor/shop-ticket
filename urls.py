from django.conf.urls.defaults import *

from satchmo_store.urls import urlpatterns as satchmo_urls

urlpatterns = patterns('',
        url('^featured/', 'localsite.views.display_featured', name='localsite_featured'),
        )

urlpatterns += satchmo_urls
