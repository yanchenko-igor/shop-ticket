from satchmo_store.shop import signals as store_signals
from payment import signals as payment_signals
from signals_ahoy.signals import application_search
from localsite.exceptions import IsReservedOrSoldError
from django.contrib.sites.models import Site
from product.models import Product, Category
from localsite.models import EventDate, HallScheme, Event
#from payment.forms import PaymentContactInfoForm
from satchmo_store.accounts.forms import RegistrationForm
from payment.views.contact import PaymentContactInfoForm
from django.db.models.signals import post_save
from django.db.models import Q
from signals_ahoy.signals import form_init, form_presave
from lxml import etree
from django import forms
from django.core.cache import cache
from django.utils.translation import ugettext as _

def update_ticket_status(sender, order=None, **kwargs):
    for item in order.orderitem_set.all():
        product = item.product
        p_types = product.get_subtypes()

        if 'Ticket' in p_types:
            if product.ticket.status == 'freely':
                product.ticket.update_status('reserved')
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


def hall_scheme_saved(sender, instance, created, raw, using, **kwargs):
    from localsite.models import SeatSection, SeatGroup, SeatLocation
    if not instance.map:
        instance.substrate.seek(0)
        xml = instance.substrate.read()
        myxml = etree.fromstring(xml.encode('UTF-8'))
        if not myxml.attrib.has_key('viewBox'):
            width = myxml.attrib['width']
            height = myxml.attrib['height']
            myxml.attrib['viewBox'] = "0 0 %i %i" % (width, height)
            del myxml.attrib['width']
            del myxml.attrib['height']
        for i in myxml.iter():
            if i.attrib.has_key('row'):
                for k in i.iter():
                    if k.attrib.has_key('ticket'):
                        k.attrib['row'] = i.attrib['row']
            if i.attrib.has_key('pricegroup'):
                for k in i.iter():
                    if k.attrib.has_key('ticket'):
                        k.attrib['pricegroup'] = i.attrib['pricegroup']
            if i.attrib.has_key('section'):
                for k in i.iter():
                    if k.attrib.has_key('ticket'):
                        k.attrib['section'] = i.attrib['section']
            
        for i in myxml.iter():
            if i.attrib.has_key('ticket'):
                i.attrib['col'] = i.getchildren()[1].getchildren()[0].text
                i.attrib['onmouseover'] = "mouseover(this);"
                i.attrib['onmouseout'] = "mouseout(this);"
                i.attrib['onclick'] = "click(this);"
                i.attrib['cursor'] = "pointer"
        script = etree.Element('script', attrib={'type':"text/ecmascript"})
        script.text = etree.CDATA("""
              function mouseover(_this) {
                  var child = _this.firstElementChild;
                  if (child.getAttribute("stroke")!='black') {
                      child.setAttribute("stroke-old",child.getAttribute("stroke"));
                      child.setAttribute("stroke-width-old",child.getAttribute("stroke-width"));
                      child.setAttribute("stroke","black");
                      child.setAttribute("stroke-width","3");
                  }
              }
              function mouseout(_this) {
                  var child = _this.firstElementChild;
                  child.setAttribute("stroke",child.getAttribute("stroke-old"));
                  child.setAttribute("stroke-width",child.getAttribute("stroke-width-old"));
              }
              function click(_this) {
                  top.add_ticket(_this.getAttribute("id"));
              }
        """)
        myxml.insert(0, script)
        to_insert = {'sections': {}, 'pricegroups': {}, 'places': []}
        for i in myxml.iter():
            if i.attrib.has_key('ticket'):
                section=i.attrib['section']
                pricegroup=i.attrib['pricegroup']
                row=i.attrib['row']
                col=i.attrib['col']
                slug=i.attrib['id']
                to_insert['sections'][section]=None
                to_insert['pricegroups'][pricegroup]=None
                to_insert['places'].append({'section':section,'pricegroup':pricegroup,'col':col,'row':row,'slug':slug})
        for k in to_insert['sections'].keys():
            try:
                section=SeatSection.objects.get(hallscheme=instance, slug=k)
            except:
                section=SeatSection.objects.create(hallscheme=instance, name=k, slug=k)
                section.save()
            to_insert['sections'][k] = section
        for k in to_insert['pricegroups'].keys():
            try:
                group=SeatGroup.objects.get(hallscheme=instance, slug=k)
            except:
                group=SeatGroup.objects.create(hallscheme=instance, name=k, slug=k)
                group.save()
            to_insert['pricegroups'][k] = group
    
        try:
            SeatLocation.objects.bulk_create([
                SeatLocation(
                            hallscheme=instance,
                            section=to_insert['sections'][place['section']],
                            group=to_insert['pricegroups'][place['pricegroup']],
                            row=place['row'],
                            col=place['col'],
                            slug=place['slug'],
                        ) for place in to_insert['places']
                ])
        except:
            pass
        xml = etree.tostring(myxml)
        instance.map = xml
        instance.save()

def event_date_saved(sender, instance, created, raw, using, **kwargs):
    if created:
        instance.map = instance.event.hallscheme.map
        instance.save()

def first_name_field_label(signal, sender, form, **kwargs):
    form.fields['first_name'].label = _('First name, Last name')

def last_name_not_required(signal, sender, form, **kwargs):
    form.fields['last_name'].required = False

def add_notes_field(signal, sender, form, **kwargs):
    if 'notes' not in form.fields:
        form.fields['notes'] = forms.CharField(label=_('Additional information'), required=False,
                widget=forms.Textarea())
    form.fields['street1'].label = _('Shipping Address')
    form.fields['copy_address'] = forms.BooleanField(initial=True, widget=forms.widgets.HiddenInput())

def split_username(signal, sender, form, **kwargs):
    if not form.cleaned_data['last_name']:
        cleaned_name = form.cleaned_data['first_name'].strip()
        if  ' ' in cleaned_name:
            form.cleaned_data['first_name'], form.cleaned_data['last_name'] = cleaned_name.split(None, 1)
        else:
            form.cleaned_data['first_name'] = cleaned_name

def clean_cache(sender, instance, created, raw, using, **kwargs):
    cache.clear()

def start_localsite_listening():
    store_signals.satchmo_cart_add_verify.connect(check_ticket_status)
    #signals.satchmo_cart_add_complete.connect(update_ticket_status)
    #payment_signals.confirm_sanity_check.connect(update_ticket_status)
    store_signals.order_success.connect(update_ticket_status)
    application_search.connect(no_tickets_search_listener, sender=Product)
    post_save.connect(clean_cache, sender=Event, dispatch_uid="event_saved")
    post_save.connect(clean_cache, sender=Product, dispatch_uid="product_saved")
    post_save.connect(event_date_saved, sender=EventDate, dispatch_uid="event_date_saved")
    post_save.connect(hall_scheme_saved, sender=HallScheme, dispatch_uid="hall_scheme_saved")
    form_init.connect(add_notes_field, sender=PaymentContactInfoForm)
    form_init.connect(first_name_field_label, sender=PaymentContactInfoForm)
    form_init.connect(first_name_field_label, sender=RegistrationForm)
    form_init.connect(last_name_not_required, sender=RegistrationForm)
    form_presave.connect(split_username, sender=PaymentContactInfoForm)
    form_presave.connect(split_username, sender=RegistrationForm)

