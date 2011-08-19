from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import user_passes_test
from django.contrib.formtools.wizard.views import SessionWizardView
from localsite.models import City, Hall, HallScheme, Event, SeatGroupPrice
from localsite.forms import EventForm2, EventForm3, make_eventform4

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

class EventWizard(SessionWizardView):
    def done(self, form_list, **kwargs):
        return render_to_response('localsite/create_event_done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })

    def get_template(self, step):
        return 'forms/wizard.html'

    def process_step(self, form):
        if self.steps.current == "0":
            if form.is_valid():
                city = form.cleaned_data['city']
                EventForm2.base_fields['hall'].queryset = Hall.objects.filter(city=city)
                self.form_list["1"] = EventForm2

        if self.steps.current == "1":
            if form.is_valid():
                hall = form.cleaned_data['hall']
                EventForm3.base_fields['hallscheme'].queryset = HallScheme.objects.filter(hall=hall)
                self.form_list["2"] = EventForm3

        if self.steps.current == "2":
            if form.is_valid():
                form_data = self.get_all_cleaned_data()

                product = Product(site_id=1, name=form_data['name'], short_description=form_data['short_description'],
                        description=form_data['description'], meta=form_data['meta'])
                product.save()
                product.category.add(*form_data['category'])
                product.related_items.add(*form_data['related_items'])
                product.save()

                hallscheme=form.cleaned_data['hallscheme']
                event = Event(product=product, hallscheme=hallscheme, tags=form_data['tags'])
                event.save()

                EventForm4 = make_eventform4(hallscheme)
                self.form_list["3"] = EventForm4

        if self.steps.current == "3":
            if form.is_valid():
                pass



        return self.get_form_step_data(form)

