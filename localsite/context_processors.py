from product.models import Category
from product.queries import bestsellers
from product.views import display_featured

def categories(request):

    ctx = {
        'root_categories': Category.objects.root_categories(),
        'bestsellers' : bestsellers(5),
        'featured' : display_featured(5, True),
    }

    return ctx
