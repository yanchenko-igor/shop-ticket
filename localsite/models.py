from django.db import models
from django.utils.translation import ugettext as _
from tagging.fields import TagField
from django.core.urlresolvers import reverse
from product.models import Option, Product, ProductPriceLookup, OptionGroup, Price ,make_option_unique_id

SATCHMO_PRODUCT=True

def get_product_types():
    return ('Event','Ticket')


# Create your models here.

class City(models.Model):
    """docstring for City"""
    name = models.CharField(max_length=25)
    slug = models.SlugField(max_length=25)
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
    
    def __unicode__(self):
        return "%s" % self.name
    

class Hall(models.Model):
    """docstring for Hall"""
    name = models.CharField(max_length=120)
    city = models.ForeignKey(City, related_name='halls')
    address = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _("Hall")
        verbose_name_plural = _("Halls")
        
    def __unicode__(self):
        return "%s" % self.name
    
    def get_absolute_url(self):
        return reverse("hall", kwargs={"hall_id": self.pk})


class HallScheme(models.Model):
    """docstring for HallScheme"""
    name = models.CharField(max_length=75)
    hall = models.ForeignKey('Hall', related_name='schemes')
    substrate = models.FileField(upload_to='substrates', max_length=100)

    
    class Meta:
        verbose_name = _("Hall Scheme")
        verbose_name_plural = _("Hall Schemes")
        
    def __unicode__(self):
        return "%s" % self.name
    
    def get_absolute_url(self):
        return reverse("view_name", kwargs={"HallScheme_id": self.pk})


class Event(models.Model):
    """docstring for Event"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    hallscheme = models.ForeignKey(HallScheme, related_name='events')
    tags = TagField()
    
    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        
    def __unicode__(self):
        return "Event: %s" % self.product.name
    
    def get_absolute_url(self):
        return reverse("event", kwargs={"slug": self.slug})

    def _get_subtype(self):
        return 'Event'

class EventDate(models.Model):
    """docstring for EventDate"""
    event = models.ForeignKey('Event', related_name='dates')
    datetime = models.DateTimeField()
    
    
    class Meta:
        verbose_name = _("Event Date")
        verbose_name_plural = _("Event Dates")
        
    
    def __unicode__(self):
        return u"%s (%s)" % (self.event, self.datetime.strftime("%d.%m.%Y %H:%M"))
    
    def get_absolute_url(self):
        return reverse("view_name", kwargs={"EventDate_id": self.pk})


class SeatGroup(models.Model):
    """docstring for SeatGroup"""
    hallscheme = models.ForeignKey('HallScheme', related_name='seatgroups')
    name = models.CharField(max_length=25)
    section = models.CharField(max_length=25)
    price = models.IntegerField()
    
    class Meta:
        verbose_name = _("Seat Group")
        verbose_name_plural = _("Seat Groups")
        
    def __unicode__(self):
        return "%s" % self.name
    
    def save(self, force_insert=False, force_update=False):
        super(SeatGroup, self).save()
        
    
    def get_absolute_url(self):
        return reverse("view_name", kwargs={"SeatGroup_id": self.pk})

class SeatLocation(models.Model):
    """docstring for SeatLocation"""
    hallscheme = models.ForeignKey('HallScheme', related_name='seats')
    group = models.ForeignKey(SeatGroup, related_name='seats')
    row = models.IntegerField(blank=True, null=True)
    col = models.IntegerField(blank=True, null=True)
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    
    class Meta:
        verbose_name = _("Seat Location")
        verbose_name_plural = _("Seat Locations")
    
    def __unicode__(self):
        if self.row and self.col:
            if self.group.section:
                return _("Section: %(sec)s (Row:%(row)s;Col:%(col)s)" % {'sec':self.group.section, 'row':self.row, 'col':self.col})
            else:
                return _("Row:%(row)s;Col:%(col)s" % {'row':self.row, 'col':self.col})
        else:
            return _("No place")
    
    def get_absolute_url(self):
        return reverse("view_name", kwargs={"SeatLocation_id": self.pk})

class Ticket(models.Model):
    """docstring for Ticket"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    parent = models.ForeignKey(Event, verbose_name=_('Parent'))
    datetime = models.ForeignKey(EventDate, related_name='tickets')
    seat = models.ForeignKey(SeatLocation)
    
    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        
    
    def __unicode__(self):
        return "Ticket: %s" % self.product.name
    
    def save(self, force_insert=False, force_update=False):
        super(Ticket, self).save()
        
    
    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def _get_subtype(self):
        return 'Ticket'

    def save(self, **kwargs):
        # don't save if the product is a configurableproduct
        if "ConfigurableProduct" in self.product.get_subtypes():
            return
        if "Event" in self.product.get_subtypes():
            return


        pvs = Ticket.objects.filter(parent=self.parent)
        pvs = pvs.exclude(product=self.product)

        for pv in pvs:
            if pv.unique_option_ids == self.unique_option_ids:
                return

        if not self.product.name:
            self.name = ""

        super(Ticket, self).save(**kwargs)
