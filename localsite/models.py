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
from lxml import etree

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
        return "%s" % self.name
    

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
        return "%s(%s)" % (self.name, self.city)
    

class SeatSection(models.Model):
    hallscheme = models.ForeignKey('HallScheme', related_name='sections')
    name = models.CharField(max_length=25)
    slug = models.SlugField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")
        unique_together = (('hallscheme', 'name'),)
        ordering = ['hallscheme', 'name']
        
    def __unicode__(self):
        return "%s - %s" % (self.hallscheme.__unicode__(), self.name)
        

class SeatGroup(models.Model):
    """docstring for SeatGroup"""
    hallscheme = models.ForeignKey('HallScheme', related_name='groups')
    name = models.CharField(max_length=25)
    slug = models.SlugField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Seat Group")
        verbose_name_plural = _("Seat Groups")
        unique_together = (('hallscheme', 'name'),('hallscheme', 'slug'),)
        ordering = ['hallscheme', 'name']
        
    def __unicode__(self):
        return "%s - %s" % (self.hallscheme.__unicode__(), self.name)
 
class SeatLocation(models.Model):
    """docstring for SeatLocation"""
    section = models.ForeignKey('SeatSection', related_name='seats')
    group = models.ForeignKey('SeatGroup', related_name='seats')
    hallscheme = models.ForeignKey('HallScheme', related_name='seats')
    row = models.IntegerField(blank=True, null=True)
    col = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Seat Location")
        verbose_name_plural = _("Seat Locations")
        unique_together = (("section", 'row', "col"),)#("section","slug"))
        ordering = ['section', 'row', 'col']
    
    def __unicode__(self):
        return "%s-%s-%s" % (self.section_id, self.row, self.col)
    

class HallScheme(models.Model):
    """docstring for HallScheme"""
    name = models.CharField(max_length=75)
    hall = models.ForeignKey('Hall', related_name='schemes')
    map = models.TextField(blank=True, null=True, editable=False)
    substrate = models.FileField(upload_to='substrates', max_length=100)

    class Meta:
        verbose_name = _("Hall Scheme")
        verbose_name_plural = _("Hall Schemes")
        unique_together = (('name', 'hall'),)
        ordering = ['hall', 'name']
        
    def __unicode__(self):
        return "%s: %s" % (self.hall.__unicode__(), self.name)
    
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

    def _get_subtype(self):
        return 'Event'

    def _get_all_prices(self):
        if not hasattr(self, '_all_prices'):
            self._all_prices = Price.objects.filter(product__ticket__in=self.tickets.all()).distinct().values('price').order_by('price')
        return self._all_prices
    all_prices = property(_get_all_prices)

    def _get_tags(self):
        return Tag.objects.get_for_object(self)
    taglist = property(_get_tags)


    def create_all_variations(self):
        myslug = self.product.slug
        myname=self.product.name
        site = self.product.site
        to_insert = {'variants':[]}
        for date in self.dates.all():
             for group in self.hallscheme.groups.all():
                 for seat in group.seats.all():
                     slug = slugify(cyr2lat('%s_%s_%s' % (myslug, date.__unicode__(), seat.__unicode__())))
                     name=u"%s :: %s :: %s" % (myname, date.__unicode__(), seat.__unicode__())
                     to_insert['variants'].append({'name':name, 'slug':slug, 'date':date, 'seat':seat})
        products = Product.objects.bulk_create([
            Product(
                site=site,
                name=u"%s :: %s :: %s" % (myname, variant['date'].__unicode__(), variant['seat'].__unicode__()),
                items_in_stock=1,
                active=True,
                slug="%s" % slugify(cyr2lat('%s_%s_%s' % (myslug,  variant['date'].__unicode__(), variant['seat'].__unicode__())))
                ) for variant in to_insert['variants']
            ])
        to_insert['products'] = {p.slug: Product.objects.get(slug=p.slug) for p in products}
        Ticket.objects.bulk_create([
            Ticket(
                product=to_insert['products'][variant['slug']],
                event=self,
                datetime=variant['date'],
                seat=variant['seat']
                ) for variant in to_insert['variants']
            ])
        Price.objects.bulk_create([
            Price(
                product=to_insert['products'][variant['slug']],
                quantity='1',
                price=self.prices.filter(group=variant['seat'].group).values('price')[0]['price'],
                ) for variant in to_insert['variants']
            ])
        

class EventDate(models.Model):
    """docstring for EventDate"""
    event = models.ForeignKey('Event', related_name='dates')
    datetime = models.DateTimeField()
    map = models.TextField(blank=True, null=True, editable=False)
    
    class Meta:
        verbose_name = _("Event Date")
        verbose_name_plural = _("Event Dates")
        unique_together = (('event', 'datetime'),)
        ordering = ['datetime', 'event']
    
    def __unicode__(self):
        return u"%s %s" % (self.event.__unicode__(), self.datetime.strftime("%d.%m.%Y %H:%M"))
    
    def update_status(self, slug, status):
        xml_obj = etree.fromstring(self.map)
        for item in xml_obj.iter():
            if item.attrib.has_key('ticket'):
                if item.attrib['id'] == slug:
                    child = item.getchildren()[0]
                    if status == 'reserved':
                        child.attrib['fill'] = '#ff8d8d'
                    elif status == 'sold':
                        child.attrib['fill'] = '#8c8c8c'
        self.map = etree.tostring(xml_obj)
        self.save()

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

    def update_status(self, status):
        if self.status != status:
            self.status = status
            self.datetime.update_status(self.seat.slug, self.status)
            self.save()

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
