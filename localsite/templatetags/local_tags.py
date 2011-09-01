from django import template
from product.models import Product
from product.queries import bestsellers
register = template.Library()

@register.inclusion_tag('localsite/product_items.html')
def show_new_arrivals(number):
    items = Product.objects.all().order_by('date_added')[:number]
    return {'items': items}

@register.inclusion_tag('localsite/product_items.html')
def show_featured_items(number):
    items = Product.objects.filter(featured=True)[:number]
    return {'items': items}

@register.inclusion_tag('localsite/product_items.html')
def show_bestsellers_items(number):
    items = bestsellers(number)
    return {'items': items}
