from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory
from localsite.models import *
from product.models import Product
from localsite.utils.translit import cyr2lat

EventFormInline = inlineformset_factory(Product, Event)

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.base_fields['related_items'].queryset = Product.objects.filter(id__in=Event.objects.all())
    class Meta:
        model = Product
        fields = (
                'name',
                'category',
                'short_description',
                'description',
                'meta',
                'related_items',
                'active',
                'featured',
                'ordering',
                'site',
                )


class EventForm(forms.ModelForm):
    class Meta:
        model = Event


class HallForm(forms.ModelForm):
    class Meta:
        model = Hall

class HallSchemeForm(forms.ModelForm):
    class Meta:
        model = HallScheme
        exclude = ('substrate',)

class SeatGroupPriceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SeatGroupPriceForm, self).__init__(*args, **kwargs)
        try:
            self.fields['price'].label = self.instance.group.name
        except:
            pass
    class Meta:
        model = SeatGroupPrice
        fields = ('price',)

SeatGroupPriceFormset = modelformset_factory(SeatGroupPrice, form=SeatGroupPriceForm, extra=0)

class EventDateForm(forms.ModelForm):
    class Meta:
        model = EventDate

EventDateFormInline = inlineformset_factory(Event, EventDate, form=EventDateForm, extra=3)
