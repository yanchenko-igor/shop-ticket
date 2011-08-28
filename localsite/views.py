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

def ajax_select_city(request):
    if request.method == 'POST':
        form = SelectCityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            return JsonResponse([dict([[hall.id,hall.name]]) for hall in city.halls.all()])
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
                return HttpResponseRedirect('/wizards/event/done/')
        else:
            formsets.append(ProductImageFormInline(instance=event.product))
    elif step == 'done':
        template='localsite/wizard_event_done.html'
        if not wizard:
            return HttpResponseRedirect('/wizards/event/')
        event = wizard['event']
        output['event'] = event
        step = wizard['step']
        if step != 4:
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
