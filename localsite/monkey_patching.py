from django.forms import ValidationError
from flatblocks.forms import FlatBlockForm
from lxml import etree
import new
def html_clean(self, value):
    try:
        etree.fromstring('<html>' + value + '</html>')
    except:
        raise ValidationError('not valid')
    return value
        
FlatBlockForm.base_fields['content'].clean =  new.instancemethod(html_clean, FlatBlockForm.base_fields['content'], FlatBlockForm.base_fields['content'].__class__)



