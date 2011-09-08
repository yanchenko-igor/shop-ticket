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
from django.contrib.flatpages.models import FlatPage
from satchmo_utils.thumbnail.widgets import AdminImageWithThumbnailWidget
import re

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class MyModelForm(forms.ModelForm):
    def as_p_d(self):
        return u'''<div id="%(prefix)s-row" class="dynamic-form %(prefix_wd)s">
        %(as_p)s\n<a href="javascript:void(0)" class="delete-row"></a>\n</div>''' % \
                {'as_p':self.as_p(), 'prefix':self.prefix, 'prefix_wd': self.prefix.rsplit('-', 1)[0]}

class MyDateInput(forms.DateInput):
    def render(self, name, value, attrs=None):
        result = super(MyDateInput, self).render(name, value, attrs)
        script = """<script type="text/javascript">var %(id_und)s_CAL=new Calendar({inputField:"%(id)s",dateFormat:"%%Y-%%m-%%d",trigger:"%(id)s_trigger",onSelect:function(){this.hide()}});</script>""" % {'id':attrs['id'],'id_und':attrs['id'].replace('-', '_')}
        return mark_safe(u'%s<img alt="" src="/static/images/icon_calendar.jpg" id="%s_trigger" class="icon_calendar">%s' % (result,attrs['id'],script))


class MyDateTimeInput(forms.DateTimeInput):
    def render(self, name, value, attrs=None):
        result = super(MyDateTimeInput, self).render(name, value, attrs)
        script = """<script type="text/javascript">var %(id_und)s_CAL=new Calendar({inputField:"%(id)s",dateFormat:"%%Y-%%m-%%d %%H:%%M",trigger:"%(id)s_trigger",showTime:true,onSelect:function(){this.hide()}});</script>""" % {'id':attrs['id'],'id_und':attrs['id'].replace('-', '_')}
        return mark_safe(u'%s<img alt="" src="/static/images/icon_calendar.jpg" id="%s_trigger" class="icon_calendar">%s' % (result,attrs['id'],script))

class FlatPageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FlatPageForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget = TinyMCE(attrs={'cols': 90, 'rows': 30})

    class Meta:
        model = FlatPage

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
                )

class SelectSeatGroupForm(forms.Form):
    group = forms.ModelChoiceField(queryset=SeatGroup.objects.all(), empty_label=_("Select section"), widget=forms.Select(attrs={'onChange':"get_values(this, '#id_ticket', '/ajax_select_group/')"}))

class SelectCityForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all(), empty_label=None, widget=forms.Select(attrs={'onChange':"get_values(this, '#id_hall', '/ajax_select_city/')"}))

class SelectEventForm(forms.Form):
    category = forms.ModelChoiceField(required=False, queryset=Category.objects.all(), empty_label=_('Category genre'))
    hall = MyModelChoiceField(required=False, queryset=City.objects.all()[0].halls.all(), empty_label=_('Hall of event'))
    min_price = forms.IntegerField(required=False, )
    max_price = forms.IntegerField(required=False, )
    min_date = forms.DateField(required=False, widget=MyDateInput(attrs={'class':'input_calendar'}))
    max_date = forms.DateField(required=False, widget=MyDateInput(attrs={'class':'input_calendar'}))


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

SeatGroupPriceFormset = modelformset_factory(SeatGroupPrice, form=SeatGroupPriceForm, extra=0, max_num=1)

class AnnouncementForm(MyModelForm):
    def __init__(self, *args, **kwargs):
        super(AnnouncementForm, self).__init__(*args, **kwargs)
        self.fields['begin'].widget = MyDateTimeInput()
        self.fields['end'].widget = MyDateTimeInput()
    class Meta:
        model = Announcement
        exclude = ('ordering',)

class EventDateForm(MyModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDateForm, self).__init__(*args, **kwargs)
        self.fields['datetime'].widget = MyDateTimeInput()
    class Meta:
        model = EventDate

class ProductImageForm(MyModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductImageForm, self).__init__(*args, **kwargs)
        self.fields['picture'].widget = AdminImageWithThumbnailWidget()
    class Meta:
        model = ProductImage
        exclude = ('sort',)

class MyBaseInlineFormSet(BaseInlineFormSet):
    def as_p_d(self):
        forms = u' '.join([form.as_p_d() for form in self])
        return mark_safe(u'\n'.join([unicode(self.management_form),
            forms, '<p><a href="javascript:void(0)" class="add-row %(prefix)s">add</a></p>' % {'prefix': self.prefix}]))

class MyBaseInlineFormSet1(BaseInlineFormSet):
    def as_p_d(self):
        return mark_safe("<fieldset>%s</fieldset>" % self.as_p())

EventDateFormInline = inlineformset_factory(Event, EventDate, form=EventDateForm, formset=MyBaseInlineFormSet, extra=1, can_delete=False, max_num=1)
AnnouncementFormInline = inlineformset_factory(Event, Announcement, form=AnnouncementForm, formset=MyBaseInlineFormSet1, extra=1, can_delete=False, max_num=1)
ProductImageFormInline = inlineformset_factory(Product, ProductImage, form=ProductImageForm, formset=MyBaseInlineFormSet, extra=1, can_delete=False, max_num=1)
EventFormInline = inlineformset_factory(Product, Event, can_delete=False, formset=MyBaseInlineFormSet1)
