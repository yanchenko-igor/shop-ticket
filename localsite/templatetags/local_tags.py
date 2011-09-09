from django import template
from product.models import Product
from product.queries import bestsellers
from localsite.forms import SelectEventDateForm
from localsite.forms import SelectSeatGroupForm
from localsite.forms import SelectTicketForm
from localsite.models import SeatSection
from localsite.models import Ticket
register = template.Library()

@register.inclusion_tag('localsite/product_items.html')
def show_new_arrivals(number):
    items = Product.objects.all().order_by('date_added')[:number]
    return {'items': items}

@register.inclusion_tag('localsite/product_items.html')
def show_featured_items(number):
    items = Product.objects.filter(featured=True)[:number]
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
    form = SelectSeatGroupForm()
    form.fields['group'].queryset = SeatSection.objects.filter(hallscheme=event.hallscheme)
    forms.append(form)
    form = SelectTicketForm()
    form.fields['ticket'].queryset = Ticket.objects.filter(event=event)
    forms.append(form)
    return {'forms': forms}
