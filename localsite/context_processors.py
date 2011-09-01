from product.models import Category
from product.models import Product
from product.queries import bestsellers
from product.views import display_featured
from localsite.forms import SelectCityForm
from localsite.forms import SelectEventForm
from localsite.models import Announcement

def categories(request):

    ctx = {
        'root_categories': Category.objects.root_categories(),
        'recent' : Product.objects.recent_by_site()[:6],
        'select_city_form': SelectCityForm(),
        'select_event_form': SelectEventForm(),
        'announcements': Announcement.objects.active(),
    }

    return ctx
