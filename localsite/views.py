from django.shortcuts import render_to_response
from django.template import RequestContext
from livesettings import config_value
from product.models import Product
from django.core.paginator import Paginator, InvalidPage
from django.contrib.auth.decorators import user_passes_test
from django.contrib.formtools.wizard.views import SessionWizardView
from localsite.models import City, Hall
from localsite.forms import EventForm2

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

        return self.get_form_step_data(form)

