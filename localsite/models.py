from django.db import models
from django.utils.translation import ugettext as _
from tagging.fields import TagField
from django.core.urlresolvers import reverse
from product.models import Option, Product, ProductPriceLookup, OptionGroup, Price ,make_option_unique_id
from satchmo_utils import cross_list

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
        return u"%s" % self.name
    

class Hall(models.Model):
    """docstring for Hall"""
    name = models.CharField(max_length=120)
    city = models.ForeignKey(City, related_name='halls')
    address = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = _("Hall")
        verbose_name_plural = _("Halls")
        
    def __unicode__(self):
        return u"%s(%s)" % (self.name, self.city)
    
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
        return u"%s: %s" % (self.hall, self.name)
    
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
        return u"Event: %s" % self.product.name
    
    def get_absolute_url(self):
        return reverse("event", kwargs={"slug": self.slug})

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
        for seat in self.hallscheme.seats.all():
            sublist.append(seat)
        masterlist.append(sublist)
        sublist = []
        for date in self.dates.all():
            sublist.append(date)
        masterlist.append(sublist)
        sublist = []
        return cross_list(masterlist)

    def create_variation(self, datetime, seat):
        site = self.product.site

        variant = Product(site=site, items_in_stock=1)
        if not slug:
            slug = slugify(u'%s_%s_%s' % (self.product.slug, datetime, seat))

        while Product.objects.filter(slug=slug).count():
            slug = u'_'.join((slug, unicode(self.product.id)))

        variant.slug = slug
        variant.save()

        ticket = Ticket(product=variant, parent=self)
        ticket.save()

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
        
    def __unicode__(self):
        return u"%s" % self.name
    
    def save(self, force_insert=False, force_update=False):
        super(SeatGroup, self).save()
        
class SeatGroupPrice(models.Model):
    """docstring for SeatGroupPrice"""
    group = models.ForeignKey(SeatGroup, related_name='prices')
    event = models.ForeignKey(Event, related_name='prices')
    price = models.IntegerField()
    
    class Meta:
        verbose_name = _("Seat Group Price")
        verbose_name_plural = _("Seat Group Prices")
    
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
    
    def __unicode__(self):
        if self.row and self.col:
            return "%s-%s-%s" % (self.group.section, self.row, self.col)
        else:
            return "No place"
    
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

