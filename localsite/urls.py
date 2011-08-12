from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r'example/', 'store.localsite.views.example', {}),
)
