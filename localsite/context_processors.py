from product.models import Category
from localsite.forms import SelectCityForm
from localsite.forms import SelectEventForm
from localsite.models import Announcement
from django.contrib.flatpages.models import FlatPage
from satchmo_ext.newsletter.forms import NewsletterForm

def categories(request):

    ctx = {
        'root_categories': Category.objects.root_categories(),
        'select_city_form': SelectCityForm(),
        'select_event_form': SelectEventForm(),
        'announcements': Announcement.objects.active(),
        'about_page': FlatPage.objects.get(id=1),
        'help_page': FlatPage.objects.get(id=2),
        'cooperation_page': FlatPage.objects.get(id=3),
        'sitemap_page': FlatPage.objects.get(id=4),
        'news_page': FlatPage.objects.get(id=5),
        'subscriptionform': NewsletterForm(),
    }

    return ctx
