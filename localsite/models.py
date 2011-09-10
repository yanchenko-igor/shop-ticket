from django.db import models
from django.db.models import Max, Min
from django.utils.translation import ugettext as _
from tagging.fields import TagField
from tagging.models import Tag
from django.core.urlresolvers import reverse
from product.models import Option, Product, ProductPriceLookup, OptionGroup, Price ,make_option_unique_id
from satchmo_utils import cross_list
from satchmo_utils.unique_id import slugify
from localsite.utils.translit import cyr2lat
from tinymce import models as tinymce_models
import datetime

SATCHMO_PRODUCT=True

def get_product_types():
    return ('Event','Ticket')


# Create your models here.

class City(models.Model):
    """docstring for City"""
    name = models.CharField(max_length=25, unique=True)
    slug = models.SlugField(max_length=25)
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in city display"))
    
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['ordering', 'name']
    
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
        ordering = ['city', 'name']
        
    def __unicode__(self):
        return u"%s(%s)" % (self.name, self.city)
    
class HallScheme(models.Model):
    """docstring for HallScheme"""
    name = models.CharField(max_length=75)
    hall = models.ForeignKey('Hall', related_name='schemes')
    substrate = models.FileField(upload_to='substrates', max_length=100)

    
    class Meta:
        verbose_name = _("Hall Scheme")
        verbose_name_plural = _("Hall Schemes")
        unique_together = (('name', 'hall'),)
        ordering = ['hall', 'name']
        
    def __unicode__(self):
        return u"%s: %s" % (self.hall, self.name)
    
class EventManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(max_date__gte=datetime.datetime.now(), product__active=True, **kwargs)

class Event(models.Model):
    """docstring for Event"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    hallscheme = models.ForeignKey(HallScheme, verbose_name=_('Hall Scheme'), related_name='events')
    min_price = models.IntegerField(null=True, blank=True, editable=False)
    max_price = models.IntegerField(null=True, blank=True, editable=False)
    min_date = models.DateField(null=True, blank=True, editable=False)
    max_date = models.DateField(null=True, blank=True, editable=False)
    tags = TagField()
    
    objects = EventManager()

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ['min_date', 'max_date']
        
    def __unicode__(self):
        return u"Event: %s" % self.product.name
    
    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def save(self, *args, **kwargs):
        dates = self.dates.aggregate(Min('datetime'), Max('datetime'))
        prices = self.prices.aggregate(Min('price'), Max('price'))
        if dates['datetime__min']:
            self.min_date = dates['datetime__min'].date()
        if dates['datetime__max']:
            self.max_date = dates['datetime__max'].date()
        self.min_price = prices['price__min']
        self.max_price = prices['price__max']
        super(Event, self).save(*args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

    def _get_subtype(self):
        return 'Event'

    def _get_tags(self):
        return Tag.objects.get_for_object(self)
    taglist = property(_get_tags)

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
        for section in self.hallscheme.sections.all():
            for group in section.groups.all():
                for seat in group.seats.all():
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
            ticket.event = self
            ticket.datetime = datetime
            ticket.seat = seat
            ticket.save()
        else:
            ticket = Ticket(product=variant, event=self)
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
        ordering = ['datetime', 'event']
    
    def __unicode__(self):
        return u"%s %s" % (self.event.__unicode__(), self.datetime.strftime("%d.%m.%Y %H:%M"))
    
    def save(self, *args, **kwargs):
        super(EventDate, self).save(*args, **kwargs)
        if not self.event.min_date:
            self.event.min_date = self.datetime.date()
            self.event.save()
        elif self.datetime.date() < self.event.min_date:
            self.event.min_date = self.datetime.date()
            self.event.save()
        if not self.event.max_date:
            self.event.max_date = self.datetime.date()
            self.event.save()
        elif self.datetime.date() > self.event.max_date:
            self.event.max_date = self.datetime.date()
            self.event.save()


class SeatSection(models.Model):
    hallscheme = models.ForeignKey('HallScheme', related_name='sections')
    name = models.CharField(max_length=25)
    
    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        unique_together = (('hallscheme', 'name'),)
        ordering = ['hallscheme', 'name']
        
    def __unicode__(self):
        return u"%s - %s" % (self.hallscheme.__unicode__(), self.name)
        

class SeatGroup(models.Model):
    """docstring for SeatGroup"""
    section = models.ForeignKey(SeatSection, related_name='groups')
    name = models.CharField(max_length=25)
    
    class Meta:
        verbose_name = _("Seat Group")
        verbose_name_plural = _("Seat Groups")
        unique_together = (('section', 'name'),)
        ordering = ['section', 'name']
        
    def __unicode__(self):
        return u"%s - %s" % (self.section.__unicode__(), self.name)
        
class SeatGroupPrice(models.Model):
    """docstring for SeatGroupPrice"""
    group = models.ForeignKey(SeatGroup, related_name='prices')
    event = models.ForeignKey(Event, related_name='prices')
    price = models.IntegerField(blank=True, null=True)
    
    class Meta:
        verbose_name = _("Seat Group Price")
        verbose_name_plural = _("Seat Group Prices")
        unique_together = (('group', 'event'),)
        ordering = ['event', 'group']
    
    def __unicode__(self):
        return u"%s - %s - %s" % (self.event.product.name, self.group.name, self.price)

    def save(self, *args, **kwargs):
        if self.price < self.event.min_price:
            self.event.min_price = self.price
            self.event.save()
        elif self.price > self.event.max_price:
            self.event.max_price = self.price
            self.event.save()
        super(SeatGroupPrice, self).save(*args, **kwargs)

class SeatLocation(models.Model):
    """docstring for SeatLocation"""
    group = models.ForeignKey(SeatGroup, related_name='seats')
    row = models.IntegerField(blank=True, null=True)
    col = models.IntegerField(blank=True, null=True)
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    
    class Meta:
        verbose_name = _("Seat Location")
        verbose_name_plural = _("Seat Locations")
        unique_together = (("group", 'row', "col"),)
        ordering = ['group', 'row', 'col']
    
    def __unicode__(self):
        if self.row and self.col:
            return "%s-%s-%s" % (self.group.section.__unicode__(), self.row, self.col)
        else:
            return "No place"
    
STATUS_CHOICES = (
        ('freely', _('Freely')),
        ('reserved', _('Reserved')),
        ('sold', _('Sold')),
        )
class Ticket(models.Model):
    """docstring for Ticket"""
    product = models.OneToOneField(Product, verbose_name=_('Product'), primary_key=True)
    event = models.ForeignKey(Event, verbose_name=_('Event'), related_name='tickets')
    datetime = models.ForeignKey(EventDate, related_name='tickets')
    seat = models.ForeignKey(SeatLocation)
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='freely')
    
    
    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        ordering = ['datetime', 'event']
        unique_together = (
                ("product", "datetime", 'seat'),
                ("event", "datetime", 'seat'),
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

class AnnouncementManager(models.Manager):
    def active(self, **kwargs):
        return self.filter(begin__lte=datetime.datetime.now(), end__gte=datetime.datetime.now(), **kwargs)

class Announcement(models.Model):
    """docstring for Announcement"""
    begin = models.DateTimeField(_("Begin"), blank=True, null=True)
    end = models.DateTimeField(_("End"), blank=True, null=True)
    event = models.ForeignKey('Event', verbose_name=_("Event"), related_name='announcements')
    text = models.TextField()
    ordering = models.IntegerField(_("Ordering"), default=0, help_text=_("Override alphabetical order in announcement display"))

    objects = AnnouncementManager()
    
    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ['ordering', 'begin']
    
    def __unicode__(self):
        begin = self.begin.strftime('%Y.%m.%d')
        end = self.end.strftime('%Y.%m.%d')

        return "%s (%s - %s)" % (self.event.product.name, begin, end)

    def save(self, **kwargs):
        if not self.begin:
            self.begin=datetime.datetime.now()
        if not self.end:
            self.end=self.begin + datetime.timedelta(days=7)
        super(Announcement, self).save(**kwargs)


from localsite.listeners import start_localsite_listening
start_localsite_listening()
