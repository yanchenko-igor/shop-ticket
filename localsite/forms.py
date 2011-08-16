from django import forms

class EventForm(forms.Form):
    """docstring"""
    name = forms.CharField(max_length=100, min_length=10)

