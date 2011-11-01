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
from signals_ahoy.signals import form_initialdata
from payment.forms import ContactInfoForm, PaymentContactInfoForm
from satchmo_store.contact.models import Contact
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
    #form = SelectSectionForm()
    #form.fields['section'].queryset = SeatSection.objects.filter(hallscheme=event.hallscheme)
    #forms.append(form)
    #form = SelectTicketForm()
    #form.fields['ticket'].queryset = Ticket.objects.none()
    #forms.append(form)
    return {'forms': forms, 'event': event}

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

def contact_form(context):
    request = context['request']
    cart = context['cart']
    shop = context['shop']

    init_data = {}
    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None

    if contact:
        for item in contact.__dict__.keys():
            init_data[item] = getattr(contact,item)
        if contact.shipping_address:
            for item in contact.shipping_address.__dict__.keys():
                init_data["ship_"+item] = getattr(contact.shipping_address,item)
        if contact.billing_address:
            for item in contact.billing_address.__dict__.keys():
                init_data[item] = getattr(contact.billing_address,item)
        if contact.primary_phone:
            init_data['phone'] = contact.primary_phone.phone
    else:
        request.session.set_test_cookie()

    if request.user.is_authenticated():
        if request.user.email:
            init_data['email'] = request.user.email
        if request.user.first_name:
            init_data['first_name'] = request.user.get_full_name()

    form_initialdata.send(sender=PaymentContactInfoForm, initial=init_data,
        contact=contact, cart=cart, shop=shop)

    form = PaymentContactInfoForm(
        cart=cart,
        shop=shop,
        contact=contact,
        initial=init_data)
    return {
            'form': form,
    }
register.inclusion_tag('localsite/block_contact_form.html', takes_context=True)(contact_form)
