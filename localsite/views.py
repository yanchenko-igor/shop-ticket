from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import user_passes_test
from django.contrib.formtools.wizard.views import SessionWizardView
from localsite.models import City, Hall, HallScheme, Event, SeatGroupPrice
from localsite.forms import *
from django.http import HttpResponseRedirect

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

@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def wizard_event_step0(request, template='localsite/wizard_event.html'):
    wizard = request.session.get('wizard')
    if not wizard:
        wizard = {}

    product = Product()

    if request.method == 'POST':

        productform = ProductForm(request.POST, instance=product)
        producteventformset = EventFormInline(request.POST, instance=product)
        if productform.is_valid() and producteventformset.is_valid():
            productform.save()
            producteventformset.save()
            wizard['product'] = productform.instance
            event = producteventformset.instance.event
            wizard['event'] = event
            wizard['step'] = 1
            request.session['wizard'] = wizard
            for group in event.hallscheme.seatgroups.all():
                price = SeatGroupPrice(event=event, group=group)
                price.save()
            return HttpResponseRedirect('/wizards/event/step1/')
    else:
        productform = ProductForm(instance=product)
        producteventformset = EventFormInline(instance=product)

    ctx = RequestContext(request, {
        'form' : productform,
        'formsets' : [producteventformset,]
    })
    return render_to_response(template, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def wizard_event_step1(request, template='localsite/wizard_event.html'):
    wizard = request.session.get('wizard')
    if not wizard:
        HttpResponseRedirect('/wizards/event/')
    event = wizard['event']

    if request.method == 'POST':

        priceformset = SeatGroupPriceFormset(request.POST, queryset=event.prices.all())
        if priceformset.is_valid():
            priceformset.save()
            wizard['step'] = 2
            return HttpResponseRedirect('/wizards/event/step2/')
    else:
        priceformset = SeatGroupPriceFormset(queryset=event.prices.all())

    ctx = RequestContext(request, {
        'form' : priceformset,
    })
    return render_to_response(template, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def wizard_event_step2(request, template='localsite/wizard_event.html'):
    wizard = request.session.get('wizard')
    if not wizard:
        HttpResponseRedirect('/wizards/event/')
    event = wizard['event']

    if request.method == 'POST':

        dateformset = EventDateFormInline(request.POST, instance=event)
        if dateformset.is_valid():
            dateformset.save()
            wizard['step'] = 3
            return HttpResponseRedirect('/wizards/event/done/')
    else:
        dateformset = EventDateFormInline(instance=event)

    ctx = RequestContext(request, {
        'form' : dateformset,
    })
    return render_to_response(template, context_instance=ctx)


@user_passes_test(lambda u: u.is_staff, login_url='/admin/')
def wizard_event_done(request, template='localsite/wizard_event_done.html'):
    wizard = request.session.get('wizard')
    if not wizard:
        HttpResponseRedirect('/wizards/event/')
    event = wizard['event']
    
    event.create_all_variations()

    del request.session['wizard']

    ctx = RequestContext(request, {})
    return render_to_response(template, context_instance=ctx)

