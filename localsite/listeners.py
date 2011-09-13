from satchmo_store.shop import signals as store_signals
from payment import signals as payment_signals
from signals_ahoy.signals import application_search
from localsite.exceptions import IsReservedOrSoldError
from django.contrib.sites.models import Site
from product.models import Product, Category
from django.db.models import Q

def update_ticket_status(sender, order=None, **kwargs):
    for item in order.orderitem_set.all():
        product = item.product
        p_types = product.get_subtypes()

        if 'Ticket' in p_types:
            if product.ticket.status == 'freely':
                product.ticket.status = 'reserved'
                product.ticket.save()
            else:
                raise Exception

def check_ticket_status(sender, cartitem=None, added_quantity=0, **kwargs):
    """Listener which vetoes adding tickets to the cart which are reserved or sold."""

    product = cartitem.product
    p_types = product.get_subtypes()

    if 'Ticket' in p_types:
        if product.ticket.status != 'freely':
            raise IsReservedOrSoldError(product, product.ticket.status)

def no_tickets_search_listener(sender, request=None, category=None, keywords=[], results={}, **kwargs):
    site = Site.objects.get_current()
    productkwargs = {}
    productkwargs['ticket__product__isnull'] = True


    if keywords:
        products = Product.objects.active_by_site(site=site, **productkwargs)
        categories = Category.objects.by_site(site=site)
    else:
        products = None
        categories = None


    if category:
        categories = Category.objects.active(site=site, slug=category)
        if categories:
            categories = categories[0].get_active_children(include_self=True)
        products.filter(category__in = categories)

    for keyword in keywords:
        if not category:
            categories = categories.filter(
                Q(name__icontains=keyword) |
                Q(meta__icontains=keyword) |
                Q(description__icontains=keyword))

        products = products.filter(
            Q(name__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(sku__iexact=keyword) )

    results.update({
        'categories': categories,
        'products': products
        })


def start_localsite_listening():
    store_signals.satchmo_cart_add_verify.connect(check_ticket_status)
    #signals.satchmo_cart_add_complete.connect(update_ticket_status)
    #payment_signals.confirm_sanity_check.connect(update_ticket_status)
    store_signals.order_success.connect(update_ticket_status)
    application_search.connect(no_tickets_search_listener, sender=Product)
