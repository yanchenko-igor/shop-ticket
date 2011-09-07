from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import user_passes_test
from django.contrib.formtools.wizard.views import SessionWizardView
from localsite.models import City, Hall, HallScheme, Event, SeatGroupPrice
from django.contrib.sites.models import Site
from localsite.forms import *
from django.http import HttpResponseRedirect
from satchmo_utils.unique_id import slugify
from localsite.utils.translit import cyr2lat
from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.db.models import Q
from satchmo_store.shop.views.sitemaps import sitemaps
from django.contrib.sitemaps.views import sitemap as django_sitemap
from django.contrib.flatpages.models import FlatPage
from sorl.thumbnail import default
from sorl.thumbnail.images import ImageFile

class JsonResponse(HttpResponse):
    def __init__(self, object):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(
                object, indent=0, cls=json.DjangoJSONEncoder,
                ensure_ascii=False)
        super(JsonResponse, self).__init__(
            content, content_type='application/json')


def flatpage_editor(request, flatpage_id, template_name='localsite/flatpage_editor.html'):
    flatpage = FlatPage.objects.get(id=flatpage_id)
    if request.method == 'POST':
        form= FlatPageForm(request.POST, instance=flatpage)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(flatpage.get_absolute_url())
    else:
        form= FlatPageForm(instance=flatpage)
    ctx = RequestContext(request, {
        'flatpage': flatpage,
        'form': form,
        })
    return render_to_response(template_name, context_instance=ctx)


def flatpages(request, template_name='localsite/flatpages.html'):
    flatpages = FlatPage.objects.all()
    ctx = RequestContext(request, {
        'flatpages': flatpages,
        })
    return render_to_response(template_name, context_instance=ctx)

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

def ajax_select_city(request):
    if request.method == 'POST':
        form = SelectCityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            return JsonResponse([{"":_('Hall of event')}] + [dict([[hall.id,hall.name]]) for hall in city.halls.all()])
    return JsonResponse([{"":_('Hall of event')}])

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
                for group in event.hallscheme.seatgroups.all():
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
