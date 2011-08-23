from django.db import models
from django.utils.translation import ugettext as _
from tagging.fields import TagField
from django.core.urlresolvers import reverse
from product.models import Option, Product, ProductPriceLookup, OptionGroup, Price ,make_option_unique_id
from satchmo_utils import cross_list
from satchmo_utils.unique_id import slugify
from localsite.utils.translit import cyr2lat

SATCHMO_PRODUCT=True

def get_product_types():
    return ('Event','Ticket')


# Create your models here.

class City(models.Model):
    """docstring for City"""
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25)
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
    
    def __unicode__(self):
        return u"%s" % self.name
    

class Hall(models.Model):
    """docstring for Hall"""
    name = models.CharField(max_length=120)
    city = models.ForeignKey(City, related_name='halls')
    address = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _("Hall")
        verbose_name_plural = _("Halls")
        unique_together = (('name', 'city'),)
        
    def __unicode__(self):
        return u"%s(%s)" % (self.name, self.city)
    
class HallScheme(models.Model):
    """docstring for HallScheme"""
    name = models.CharField(max_length=75, unique=True)
    hall = models.ForeignKey('Hall', related_name='schemes')
    substrate = models.FileField(upload_to='substrates', max_length=100)

    
    class Meta:
        verbose_name = _("Hall Scheme")
        verbose_name_plural = _("Hall Schemes")
        
    def __unicode__(self):
        return u"%s: %s" % (self.hall, self.name)
    
class Event(models.Model):
    """docstring for Event"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    hallscheme = models.ForeignKey(HallScheme, related_name='events')
    tags = TagField()
    
    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        
    def __unicode__(self):
        return u"Event: %s" % self.product.name
    
    def _get_subtype(self):
        return 'Event'

    def get_all_options(self):
        """
        Returns all possible combinations of options for this products OptionGroups as a List of Lists.
        Ex:
        For OptionGroups Color and Size with Options (Blue, Green) and (Large, Small) you'll get
        [['Blue', 'Small'], ['Blue', 'Large'], ['Green', 'Small'], ['Green', 'Large']]
        Note: the actual values will be instances of Option instead of strings
        """
        sublist = []
        masterlist = []
        #Create a list of all the options & create all combos of the options
        for date in self.dates.all():
            sublist.append(date)
        masterlist.append(sublist)
        sublist = []
        for seat in self.hallscheme.seats.all():
            sublist.append(seat)
        masterlist.append(sublist)
        sublist = []
        return cross_list(masterlist)

    def create_all_variations(self):
        """
        Get a list of all the optiongroups applied to this object
        Create all combinations of the options and create variations
        """
        # Create a new ProductVariation for each combination.
        for (datetime, seat) in self.get_all_options():
            self.create_variation(datetime, seat)

    def create_variation(self, datetime, seat, name=u"", slug=u""):
        site = self.product.site

        if not slug:
            slug = slugify(cyr2lat('%s_%s_%s' % (self.product.slug, datetime, seat)))
        if not name:
            name=u"%s :: %s :: %s" % (self.product.name, datetime.__unicode__(), seat)

        if Product.objects.filter(site=site, slug=slug):
            variant = Product.objects.get(site=site, slug=slug)
            variant.name=name
            variant.active=False
            variant.save(force_update=True)
        else:
            variant = Product(site=site, name=name, items_in_stock=1, active=False, slug=slug)
            variant.save()

        pricevalue = self.prices.filter(group=seat.group).values('price')[0]['price']
        try:
            price = Price.objects.get(product=variant, quantity='1')
        except Price.DoesNotExist:
            price = Price(product=variant, quantity='1')
        price.price = pricevalue
        price.save()

        if Ticket.objects.filter(product=variant):
            ticket = Ticket.objects.get(product=variant)
            ticket.parent = self
            ticket.datetime = datetime
            ticket.seat = seat
            ticket.save()
        else:
            ticket = Ticket(product=variant, parent=self)
            ticket.datetime = datetime
            ticket.seat = seat
            ticket.save()


class EventDate(models.Model):
    """docstring for EventDate"""
    event = models.ForeignKey('Event', related_name='dates')
    datetime = models.DateTimeField()
    
    class Meta:
        verbose_name = _("Event Date")
        verbose_name_plural = _("Event Dates")
        unique_together = (('event', 'datetime'),)
    
    def __unicode__(self):
        return u"%s" % self.datetime.strftime("%d.%m.%Y %H:%M")
    
class SeatGroup(models.Model):
    """docstring for SeatGroup"""
    hallscheme = models.ForeignKey('HallScheme', related_name='seatgroups')
    name = models.CharField(max_length=25)
    section = models.CharField(max_length=25)
    
    class Meta:
        verbose_name = _("Seat Group")
        verbose_name_plural = _("Seat Groups")
        unique_together = (('hallscheme', 'name'),)
        
    def __unicode__(self):
        return u"%s" % self.name
    
    def save(self, force_insert=False, force_update=False):
        super(SeatGroup, self).save()
        
class SeatGroupPrice(models.Model):
    """docstring for SeatGroupPrice"""
    group = models.ForeignKey(SeatGroup, related_name='prices')
    event = models.ForeignKey(Event, related_name='prices')
    price = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Seat Group Price")
        verbose_name_plural = _("Seat Group Prices")
        unique_together = (('group', 'event'),)
    
    def __unicode__(self):
        return u"%s - %s - %s" % (self.event.product.name, self.group.name, self.price)

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
        unique_together = (("hallscheme", "group", 'row', "col"),)
    
    def __unicode__(self):
        if self.row and self.col:
            return "%s-%s-%s" % (self.group.section, self.row, self.col)
        else:
            return "No place"
    
class Ticket(models.Model):
    """docstring for Ticket"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    parent = models.ForeignKey(Event, verbose_name=_('Parent'))
    datetime = models.ForeignKey(EventDate, related_name='tickets')
    seat = models.ForeignKey(SeatLocation)
    
    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        unique_together = (
                ("product", "datetime", 'seat'),
                ("parent", "datetime", 'seat'),
                )

    def __unicode__(self):
        return "Ticket: %s" % self.product.name
    
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

        if not self.product.name:
            self.name = ""

        super(Ticket, self).save(**kwargs)

