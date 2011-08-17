from django import forms
from localsite.models import City, Hall

class EventForm1(forms.Form):
    name = forms.CharField(max_length=100, min_length=10)
    city = forms.ModelChoiceField(queryset=City.objects.all())

class EventForm2(forms.Form):
    hall = forms.ModelChoiceField(queryset=Hall.objects.all())
