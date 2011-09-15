from django import template
from django.utils.safestring import mark_safe
from product.models import Product
from localsite.queries import bestsellers
from decimal import Decimal, InvalidOperation
from localsite.utils import moneyfmt
from localsite.forms import SelectEventDateForm
from localsite.forms import SelectSectionForm
from localsite.forms import SelectTicketForm
from localsite.models import SeatSection
from localsite.models import Ticket
register = template.Library()

@register.inclusion_tag('localsite/product_items.html')
def show_new_arrivals(number):
    items = Product.objects.all(ticket__product__isnull=True, ).order_by('date_added')[:number]
    return {'items': items}

@register.inclusion_tag('localsite/product_items.html')
def show_featured_items(number):
    items = Product.objects.filter(ticket__product__isnull=True, featured=True)[:number]
    return {'items': items}

@register.inclusion_tag('localsite/product_items.html')
def show_bestsellers_items(number):
    items = bestsellers(number)
    return {'items': items}

@register.inclusion_tag('localsite/block_ticket_choice.html')
def select_section_form(event):
    forms = []
    form = SelectEventDateForm()
    form.fields['datetime'].queryset = event.dates.all()
    forms.append(form)
    form = SelectSectionForm()
    form.fields['section'].queryset = SeatSection.objects.filter(hallscheme=event.hallscheme)
    forms.append(form)
    form = SelectTicketForm()
    form.fields['ticket'].queryset = Ticket.objects.none()
    forms.append(form)
    return {'forms': forms}

def price_range(product):
    p_types = product.get_subtypes()

    if 'Event' in p_types:
        if product.event.min_price == product.event.max_price:
            return product.event.min_price
        else:
            return "%s - %s" % (product.event.min_price, product.event.max_price)
    else:
        return product.unit_price


register.filter('price_range', price_range)


def range_currency(value):
    values = None
    if value == '' or value is None:
        return value

    try:
        value = Decimal(str(value))
    except InvalidOperation:
        values = [mark_safe(moneyfmt(Decimal(str(val)))) for val in value.split(' - ')]

    if values:
        return mark_safe(' - '.join(values))

    return mark_safe(moneyfmt(value, **kwargs))

register.filter('range_currency', range_currency)
range_currency.is_safe = True

def wrap_currency(value, args=""):
    if value == '' or value is None:
        return value

    try:
        value = Decimal(str(value))
    except InvalidOperation:
        log.error("Could not convert value '%s' to decimal", value)
        raise

    return mark_safe(moneyfmt(value, wrapval='label'))

register.filter('wrap_currency', wrap_currency)
wrap_currency.is_safe = True
