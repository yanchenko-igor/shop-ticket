from django import forms
from django.forms.formsets import formset_factory
from localsite.models import City, Hall, HallScheme, Event, SeatGroupPrice
from product.models import Product
from localsite.utils.translit import cyr2lat

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

class EventForm(forms.ModelForm):
    class Meta:
        model = Event

class HallForm(forms.ModelForm):
    class Meta:
        model = Hall

class HallSchemeForm(forms.ModelForm):
    class Meta:
        model = HallScheme

class SeatGroupPriceForm(forms.ModelForm):
    class Meta:
        model = SeatGroupPrice

class EventForm1(forms.Form):
    city = HallForm.base_fields['city']
    name = ProductForm.base_fields['name']
    short_description = ProductForm.base_fields['short_description']
    description = ProductForm.base_fields['description']
    category = ProductForm.base_fields['category']
    meta = ProductForm.base_fields['meta']
    related_items = ProductForm.base_fields['related_items']
    related_items.queryset = Product.objects.filter(id__in=Event.objects.all())
    tags = EventForm.base_fields['tags']

class EventForm2(forms.Form):
    hall = HallSchemeForm.base_fields['hall']

class EventForm3(forms.Form):
    hallscheme = EventForm.base_fields['hallscheme']

#class EventForm4(forms.Form):
#    pass

def make_eventform4(hallscheme):
    fields = {}
    for group in hallscheme.seatgroups.all():
        print group.name
        fields[cyr2lat(group.name)] = forms.IntegerField()
    print fields
    return type('EventForm4', (forms.Form,), fields)
