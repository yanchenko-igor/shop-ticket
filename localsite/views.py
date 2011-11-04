from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from localsite.queries import bestsellers
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import user_passes_test
from django.contrib.formtools.wizard.views import SessionWizardView
from localsite.models import HallScheme, EventDate, Event, SeatGroupPrice, Ticket
from django.contrib.sites.models import Site
from localsite.forms import AnnouncementFormInline, EventDateFormInline, EventFormInline, FlatPageForm, ProductForm, ProductImageFormInline, SeatGroupPriceFormset
from localsite.forms import SeatLocationInline, SeatSectionInline, SelectCityForm, SelectEventDateForm, SelectEventForm, SelectPlaceForm, SelectSeatGroupForm, SelectSectionForm
from django.http import HttpResponseRedirect
from satchmo_utils.unique_id import slugify
from localsite.utils.translit import cyr2lat
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.flatpages.models import FlatPage
from sorl.thumbnail import default
from sorl.thumbnail.images import ImageFile
from tagging.models import Tag, TaggedItem
from satchmo_store.shop.exceptions import CartAddProhibited
from satchmo_store.shop.models import NullCart, Cart
from satchmo_store.shop.signals import satchmo_cart_changed, satchmo_cart_add_complete, satchmo_cart_details_query
from satchmo_utils.numbers import round_decimal
from satchmo_store.shop.views.cart import _product_error
from satchmo_store.shop.views.cart import _json_response
from satchmo_store.shop.views.cart import _set_quantity
from satchmo_utils.views import bad_or_missing
from lxml import etree

@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def place_editor(request, section_id, template_name='localsite/place_editor.html'):
    section = SeatSection.objects.get(id=section_id)
    groupform = None
    if request.method == 'POST':
        formset = SeatLocationInline(request.POST, instance=section)
        if formset.is_valid():
            formset.save()
            data = {'results': _("Success")}
            return _json_response(data)
        else:
            data = {'errors': formset.errors}
            return _json_response(data)
    else:
        formset= SeatLocationInline(instance=section)
        groupform = SelectSeatGroupForm()
        groupform.fields['group'].queryset = SeatGroup.objects.filter(hallscheme__sections=section)
    ctx = RequestContext(request, {
        'section': section,
        'formset': formset,
        'groupform': groupform,
        })
    return render_to_response(template_name, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def section_editor(request, hallscheme_id, template_name='localsite/hallscheme_editor.html'):
    hallscheme = HallScheme.objects.get(id=section_id)
    if request.method == 'POST':
        formset = SeatSectionInline(request.POST, instance=hallscheme)
        if formset.is_valid():
            formset.save()
            data = {'results': _("Success")}
            return _json_response(data)
        else:
            data = {'errors': formset.errors}
            return _json_response(data)
    else:
        formset= SeatSectionInline(instance=hallscheme)
    ctx = RequestContext(request, {
        'hallscheme': hallscheme,
        'formset': formset,
        })
    return render_to_response(template_name, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def flatpage_editor(request, flatpage_id, template_name='localsite/flatpage_editor.html'):
    flatpage = FlatPage.objects.get(id=flatpage_id)
    if request.method == 'POST':
        form= FlatPageForm(request.POST, instance=flatpage)
        if form.is_valid():
            page = form.save()
            page.save()
            return HttpResponseRedirect(flatpage.get_absolute_url())
    else:
        form= FlatPageForm(instance=flatpage)
    ctx = RequestContext(request, {
        'flatpage': flatpage,
        'form': form,
        })
    return render_to_response(template_name, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def flatpages(request, template_name='localsite/flatpages.html'):
    flatpages = FlatPage.objects.all()
    ctx = RequestContext(request, {
        'flatpages': flatpages,
        })
    return render_to_response(template_name, context_instance=ctx)

def tag_detail(request, slug, template_name='localsite/tag_detail.html'):
    tag = get_object_or_404(Tag, name__iexact=slug)
    events = TaggedItem.objects.get_by_model(Event,tag)
    ctx = RequestContext(request, {
        'events': events,
        'tag': tag,
        })
    return render_to_response(template_name, context_instance=ctx)

@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def edit_event(request, event_id, template_name='localsite/edit_event.html'):
    event = Event.objects.get(product=event_id)
    formsets = []
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=event.product)
        formsets.append(EventFormInline(request.POST, instance=event.product))
        formsets.append(AnnouncementFormInline(request.POST, instance=event))
        formsets.append(EventDateFormInline(request.POST, instance=event))
        formsets.append(ProductImageFormInline(request.POST, request.FILES, instance=event.product))
        all_valid = form.is_valid()
        for formset in formsets:
            all_valid = all_valid and formset.is_valid()
        if all_valid:
            form.save()
            formsets[0].save()
            formsets[1].save()
            formsets[2].save()
            images = formsets[3].save()
            for image in images:
                default.kvstore.delete_thumbnails(ImageFile(image.picture.name))
            return HttpResponseRedirect(event.get_absolute_url())
    else:
        form = ProductForm(instance=event.product)
        formsets.append(EventFormInline(instance=event.product))
        formsets.append(AnnouncementFormInline(instance=event))
        formsets.append(EventDateFormInline(instance=event))
        formsets.append(ProductImageFormInline(instance=event.product))
    ctx = RequestContext(request, {
        'event': event,
        'form': form,
        'formsets': formsets,
        })
    return render_to_response(template_name, context_instance=ctx)

def get_hall_map(request, eventdate_id):
    eventdate = EventDate.objects.get(id=eventdate_id)
    xml = eventdate.map
    cart = Cart.objects.from_request(request, create=False)
    if not isinstance(cart, NullCart):
        cart_items = cart.cartitem_set.all()
        if cart_items:
            tickets = cart_items.filter(product__ticket__datetime=eventdate)
            if tickets:
                xml_obj = etree.fromstring(xml)
                for cart_item in tickets:
                    for item in xml_obj.iter():
                        if item.attrib.has_key('ticket'):
                            if item.attrib['id'] == cart_item.product.ticket.seat.slug:
                                child = item.getchildren()[0]
                                child.attrib['fill'] = '#a6cd77'
                                break
                xml = etree.tostring(xml_obj)


    return HttpResponse(xml, mimetype="image/svg+xml")

def display_bestsellers(request, count=0, template='product/best_sellers.html'):
    """Display a list of the products which have sold the most"""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')
    
    ctx = RequestContext(request, {
        'products' : bestsellers(count),
    })
    return render_to_response(template, context_instance=ctx)
        
def display_featured(request, page=0, count=0, template='localsite/featured.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')

    if page == 0:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
        else:
            page = 1
     
    query = Product.objects.featured_by_site(ticket__product__isnull=True)
    paginator = Paginator(query, count)
    try:
        currentpage = paginator.page(page)
    except InvalidPage:
        currentpage = None
    
    ctx = RequestContext(request, {
        'curentpage_number' : page,
        'page' : currentpage,
        'paginator' : paginator,
    })
    return render_to_response(template, context_instance=ctx)
        
def display_related(request, id, page=0, count=0, template='localsite/related.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')

    if page == 0:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
        else:
            page = 1
     
    product = Product.objects.get(id=id)
    query = product.related_items.all()
    paginator = Paginator(query, count)
    try:
        currentpage = paginator.page(page)
    except InvalidPage:
        currentpage = None
    
    ctx = RequestContext(request, {
        'curentpage_number' : page,
        'prod' : product,
        'page' : currentpage,
        'paginator' : paginator,
    })
    return render_to_response(template, context_instance=ctx)
        
def display_recent(request, page=0, count=0, template='product/recently_added.html'):
    """Display a list of recently added products."""
    if count == 0:
        count = config_value('PRODUCT','NUM_PAGINATED')

    if page == 0:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
        else:
            page = 1
     
    query = Product.objects.recent_by_site(ticket__product__isnull=True)
    paginator = Paginator(query, count)
    try:
        currentpage = paginator.page(page)
    except InvalidPage:
        currentpage = None
    
    ctx = RequestContext(request, {
        'curentpage_number' : page,
        'page' : currentpage,
        'paginator' : paginator,
    })
    return render_to_response(template, context_instance=ctx)
        
def select_event(request, template='localsite/select_event.html'):
    events = Event.objects.none()
    form_city = None
    form_event = None
    if request.method == 'POST':
        form_city = SelectCityForm(request.POST)
        if form_city.is_valid():
            city = form_city.cleaned_data['city']
            form_event = SelectEventForm(request.POST)
            form_event.fields['hall'].queryset = city.halls.all()
            if form_event.is_valid():
                hall = form_event.cleaned_data['hall']
                category = form_event.cleaned_data['category']
                min_price = form_event.cleaned_data['min_price']
                max_price = form_event.cleaned_data['max_price']
                min_date = form_event.cleaned_data['min_date']
                max_date = form_event.cleaned_data['max_date']
                events = Event.objects.active().filter(
                        min_price and Q(min_price__gte=min_price) | Q(max_price__gte=min_price) or Q(),
                        max_price and Q(max_price__lte=max_price) | Q(min_price__lte=max_price) or Q(),
                        min_date and Q(min_date__gte=min_date) | Q(max_date__gte=min_date) or Q(),
                        max_date and Q(max_date__lte=max_date) | Q(min_date__lte=max_date) or Q(),
                        hall and Q(hallscheme__hall=hall) or city and Q(hallscheme__hall__city=city) or Q(),
                        category and Q(product__category=category) or Q(),
                        )
     

    if not form_city:
        form_city = SelectCityForm()
    if not form_event:
        form_event = SelectEventForm()
    ctx = RequestContext(request, {
        'events': events,
        'form_city': form_city,
        'form_event': form_event,
    })
    return render_to_response(template, context_instance=ctx)

def add_ticket2(request, quantity=1, redirect_to='satchmo_cart'):
    formdata = request.POST.copy()
    details = []

    form1 = SelectEventDateForm(request.POST)
    form1.fields['datetime'].queryset = EventDate.objects.all()
    if form1.is_valid():
        datetime = form1.cleaned_data['datetime']
        form2 = SelectPlaceForm(request.POST)
        form2.fields['seat'].queryset = datetime.event.hallscheme.seats.all()
        if form2.is_valid():
            seat = form2.cleaned_data['seat']
            ticket = Ticket.objects.get(seat=seat, datetime=datetime)
            cart = Cart.objects.from_request(request, create=True)
            satchmo_cart_details_query.send(
                    cart,
                    product=ticket.product,
                    quantity=quantity,
                    details=details,
                    request=request,
                    form=formdata
                    )
            try:
                added_item = cart.add_item(ticket.product, number_added=1, details=details)
                added_item.quantity = 1
                added_item.save()
        
            except CartAddProhibited, cap:
                return _product_error(request, ticket.product, cap.message)
        
            # got to here with no error, now send a signal so that listeners can also operate on this form.
            satchmo_cart_add_complete.send(cart, cart=cart, cartitem=added_item, product=ticket.product, request=request, form=formdata)
            satchmo_cart_changed.send(cart, cart=cart, request=request)
        
            if request.is_ajax():
                data = {
                    'id': ticket.product.id,
                    'slug': seat.slug,
                    'name': ticket.product.translated_name(),
                    'item_id': added_item.id,
                    'item_qty': str(round_decimal(quantity, 2)),
                    'item_price': str(added_item.line_total) or "0.00",
                    'cart_count': str(round_decimal(cart.numItems, 2)),
                    'cart_total': str(round_decimal(cart.total, 2)),
                    # Legacy result, for now
                    'results': _("Success"),
                }
        
                return _json_response(data)
            else:
                return redirect(redirect_to)
        else:
            return _json_response({'errors': form2.errors, 'results': _("Error")}, True)
    else:
        return _json_response({'errors': form1.errors, 'results': _("Error")}, True)


def remove_ticket(request):
    if not request.POST:
        return bad_or_missing(request, "Please use a POST request")

    success, cart, cartitem, errors = _set_quantity(request, force_delete=True)

    if request.is_ajax():
        if errors:
            return _json_response({'errors': errors, 'results': _("Error")}, True)
        else:
            return _json_response({
                'cart_total': str(cart.total),
                'cart_count': str(cart.numItems),
                'item_id': cartitem.id,
                'results': success, # Legacy
            })

def ajax_select_ticket(request):
    if request.method == 'POST':
        form1 = SelectEventDateForm(request.POST)
        form1.fields['datetime'].queryset = EventDate.objects.all()
        if form1.is_valid():
            datetime = form1.cleaned_data['datetime']
            form2 = SelectSectionForm(request.POST)
            form2.fields['section'].queryset = datetime.event.hallscheme.sections.all()
            if form2.is_valid():
                section = form2.cleaned_data['section']
                return _json_response([{"":_('Select ticket')}] + [dict([[ticket.product.id, "%s-%s" % (ticket.__unicode__(), ticket.get_status_display())]]) for ticket in Ticket.objects.filter(seat__section=section,datetime=datetime)])
    return _json_response([{"":_('Select ticket')}])

def ajax_select_ticket2(request):
    if request.method == 'POST':
        form1 = SelectEventDateForm(request.POST)
        form1.fields['datetime'].queryset = EventDate.objects.all()
        if form1.is_valid():
            datetime = form1.cleaned_data['datetime']
            form2 = SelectSectionForm(request.POST)
            form2.fields['section'].queryset = datetime.event.hallscheme.sections.all()
            if form2.is_valid():
                section = form2.cleaned_data['section']
                cart = Cart.objects.from_request(request)
                try:
                    cartitems = cart.cartitem_set.all()
                except:
                    cartitems = None
                return _json_response([dict([[ticket.product.id,  {
                    'status': ticket.status,
                    'section': ticket.seat.section.name,
                    'col': ticket.seat.col,
                    'row': ticket.seat.row,
                    'x': ticket.seat.x_position,
                    'y': ticket.seat.y_position,
                    'price': str(ticket.product.unit_price),
                    'product': ticket.product.id,
                    'in_cart': cartitems and str(cartitems.filter(product=ticket.product).count()) or '0',
                    'cartitem_id': cartitems and cartitems.filter(product=ticket.product).count() and cartitems.filter(product=ticket.product)[0].id or None,
                    }]]) for ticket in Ticket.objects.filter(seat__section=section,datetime=datetime)])
    return _json_response([])

def ajax_select_city(request):
    if request.method == 'POST':
        form = SelectCityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            return _json_response([{"":_('Hall of event')}] + [dict([[hall.id,hall.name]]) for hall in city.halls.all()])
    return _json_response([{"":_('Hall of event')}])

@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def wizard_event(request, step='step0', template='localsite/wizard_event.html'):
    wizard = request.session.get('wizard')
    output = {}
    formsets = []
    form = None

    if step == 'step0':
        if not wizard:
            wizard = {}
        product = Product()
        if request.method == 'POST':
            form = ProductForm(request.POST, instance=product)
            formsets.append(EventFormInline(request.POST, instance=product))
            if form.is_valid() and formsets[0].is_valid():
                product = form.save(commit=False)
                product.site = Site.objects.get(id=1)
                product.slug = slugify(cyr2lat(product.name))
                product.save()
                form.save_m2m()
                formsets[0].save()
                event = formsets[0].instance.event
                wizard['event'] = event
                wizard['step'] = 1
                request.session['wizard'] = wizard
                for group in event.hallscheme.groups.all():
                    price = SeatGroupPrice(event=event, group=group)
                    price.save()
                return HttpResponseRedirect('/wizards/event/step1/')
        else:
            form = ProductForm(instance=product)
            formsets.append(EventFormInline(instance=product))
    elif step == 'step1':
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        step = wizard['step']
        if step != 1:
            return HttpResponseRedirect('/wizards/event/')
        if request.method == 'POST':
            form = SeatGroupPriceFormset(request.POST, queryset=event.prices.all())
            if form.is_valid():
                form.save()
                wizard['step'] = 2
                request.session['wizard'] = wizard
                return HttpResponseRedirect('/wizards/event/step2/')
        else:
            form = SeatGroupPriceFormset(queryset=event.prices.all())
    elif step == 'step2':
        template='localsite/wizard_event_dates.html'
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        step = wizard['step']
        if step != 2:
            return HttpResponseRedirect('/wizards/event/')
        if request.method == 'POST':
            formsets.append(EventDateFormInline(request.POST, instance=event))
            if formsets[0].is_valid():
                formsets[0].save()
                wizard['step'] = 3
                request.session['wizard'] = wizard
                return HttpResponseRedirect('/wizards/event/step3/')
        else:
            formsets.append(EventDateFormInline(instance=event))
    elif step == 'step3':
        template='localsite/wizard_product_images.html'
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        step = wizard['step']
        if step != 3:
            return HttpResponseRedirect('/wizards/event/')
        if request.method == 'POST':
            formsets.append(ProductImageFormInline(request.POST, request.FILES, instance=event.product))
            if formsets[0].is_valid():
                formsets[0].save()
                wizard['step'] = 4
                request.session['wizard'] = wizard
                return HttpResponseRedirect('/wizards/event/step4/')
        else:
            formsets.append(ProductImageFormInline(instance=event.product))
    elif step == 'step4':
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        step = wizard['step']
        if step != 4:
            return HttpResponseRedirect('/wizards/event/')
        if request.method == 'POST':
            formsets.append(AnnouncementFormInline(request.POST, request.FILES, instance=event))
            if formsets[0].is_valid():
                formsets[0].save()
                wizard['step'] = 5
                request.session['wizard'] = wizard
                return HttpResponseRedirect('/wizards/event/done/')
        else:
            formsets.append(AnnouncementFormInline(instance=event))
    elif step == 'done':
        template='localsite/wizard_event_done.html'
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        output['event'] = event
        step = wizard['step']
        if step != 5:
            return HttpResponseRedirect('/wizards/event/')
        event.create_all_variations()
        del request.session['wizard']
        return HttpResponseRedirect(event.get_absolute_url())

    if form:
        output['form'] = form
    if formsets:
        output['formsets'] = formsets
    ctx = RequestContext(request, output)
    return render_to_response(template, context_instance=ctx)
