from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from django.core.paginator import Paginator, InvalidPage

def example(request):
    ctx = RequestContext(request, {})
    return render_to_response('localsite/example.html', context_instance=ctx)
        
def display_featured(request, page=0, count=0, template='localsite/featured.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')

    if page == 0:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
        else:
            page = 1
     
    query = Product.objects.featured_by_site()
    paginator = Paginator(query, count)
    try:
        currentpage = paginator.page(page)
    except InvalidPage:
        currentpage = None
    
    ctx = RequestContext(request, {
        'page' : currentpage,
        'paginator' : paginator,
    })
    return render_to_response(template, context_instance=ctx)
