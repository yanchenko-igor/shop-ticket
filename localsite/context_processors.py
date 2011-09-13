from product.models import Category
from product.models import Product
from localsite.queries import bestsellers
from product.views import display_featured
from localsite.forms import SelectCityForm
from localsite.forms import SelectEventForm
from localsite.models import Announcement
from django.contrib.flatpages.models import FlatPage

def categories(request):

    ctx = {
        'root_categories': Category.objects.root_categories(),
        'recent' : Product.objects.recent_by_site(ticket__product__isnull=True)[:6],
        'select_city_form': SelectCityForm(),
        'select_event_form': SelectEventForm(),
        'announcements': Announcement.objects.active(),
        'about_page': FlatPage.objects.get(id=1),
        'help_page': FlatPage.objects.get(id=2),
        'cooperation_page': FlatPage.objects.get(id=3),
        'sitemap_page': FlatPage.objects.get(id=4),
        'news_page': FlatPage.objects.get(id=5),
    }

    return ctx
