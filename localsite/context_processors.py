from product.models import Category
from product.models import Product
from product.queries import bestsellers
from product.views import display_featured
from localsite.forms import SelectCityForm
from localsite.forms import SelectEventForm

def categories(request):

    ctx = {
        'root_categories': Category.objects.root_categories(),
        'bestsellers' : bestsellers(5),
        'recent' : Product.objects.recent_by_site()[:6],
        'featured' : display_featured(5, True),
        'select_city_form': SelectCityForm(),
        'select_event_form': SelectEventForm(),
    }

    return ctx
