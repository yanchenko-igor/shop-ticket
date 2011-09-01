from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms.models import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from localsite.models import *
from product.models import Product, ProductImage, Category
from localsite.utils.translit import cyr2lat
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from tinymce.widgets  import TinyMCE

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class MyModelForm(forms.ModelForm):
    def as_p_d(self):
        return u'''<div id="%(prefix)s-row" class="dynamic-form">
        %(as_p)s\n<a href="javascript:void(0)" class="delete-row"></a>\n</div>''' % \
                {'as_p':self.as_p(), 'prefix':self.prefix}

class MyDateInput(forms.DateInput):
    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs, **{'class':'input_calendar'})
        result = super(MyDateInput, self).render(name, value, final_attrs)
        script = """
                                                    <script type="text/javascript">
                                                           var %(id_und)s_CAL = new Calendar({
                                                                  inputField: "%(id)s",
                                                                  dateFormat: "%%Y-%%m-%%d",
                                                                  trigger: "%(id)s_trigger",
                                                                  onSelect   : function() { this.hide() }
                                                          });
                                                    </script>
                                                    """ % {'id':final_attrs['id'],'id_und':final_attrs['id'].replace('-', '_')}
        return mark_safe(u'%s<img alt="" src="/static/images/icon_calendar.jpg" id="%s_trigger" class="icon_calendar">%s' % (result,final_attrs['id'],script))

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.base_fields['related_items'].queryset = Product.objects.filter(id__in=Event.objects.all())
        self.fields['related_items'].queryset = Product.objects.filter(id__in=Event.objects.all())
        self.fields['description'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30})

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
                'shipclass',
                'ordering',
                )

class SelectCityForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label=None)

class SelectEventForm(forms.Form):
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.all(), empty_label=_('Category genre'))
    hall = MyModelChoiceField(required=False, queryset=City.objects.all()[0].halls.all(), empty_label=_('Hall of event'))
    min_price = forms.IntegerField(required=False, )
    max_price = forms.IntegerField(required=False, )
    min_date = forms.DateField(required=False, widget=MyDateInput())
    max_date = forms.DateField(required=False, widget=MyDateInput())


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

class EventDateForm(MyModelForm):
    class Meta:
        model = EventDate

class ProductImageForm(MyModelForm):
    class Meta:
        model = ProductImage
        exclude = ('sort',)

class MyBaseInlineFormSet(BaseInlineFormSet):
    def as_p_d(self):
        forms = u' '.join([form.as_p_d() for form in self])
        return mark_safe(u'\n'.join([unicode(self.management_form),
            forms, '<p><a href="javascript:void(0)" class="add-row">add</a></p>']))

EventDateFormInline = inlineformset_factory(Event, EventDate, form=EventDateForm, formset=MyBaseInlineFormSet, extra=1, can_delete=False)
ProductImageFormInline = inlineformset_factory(Product, ProductImage, form=ProductImageForm, formset=MyBaseInlineFormSet, extra=1, can_delete=False)
EventFormInline = inlineformset_factory(Product, Event, can_delete=False)
