from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from store.localsite.models import *
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE
from product.admin import ProductOptions
from django.utils.translation import ugettext as _

class SeatSectionInline(admin.TabularInline):
    model = SeatSection
    extra = 0

class SeatGroupInline(admin.TabularInline):
    model = SeatGroup
    extra = 0

class SeatLocationInline(admin.TabularInline):
    model = SeatLocation
    extra = 0

#class SeatSectionAdmin(admin.ModelAdmin):
#    inlines = [SeatLocationInline]
#admin.site.register(SeatSection, SeatSectionAdmin)

class HallSchemeAdmin(admin.ModelAdmin):
    inlines = [SeatSectionInline,SeatGroupInline]
admin.site.register(HallScheme, HallSchemeAdmin)

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(City, CityAdmin)

class HallAdmin(admin.ModelAdmin):
    pass
admin.site.register(Hall, HallAdmin)

class TicketAdmin(admin.ModelAdmin):
    readonly_fields = ('product','event',)
admin.site.register(Ticket, TicketAdmin)

#class SeatGroupAdmin(admin.ModelAdmin):
#    inlines = [SeatLocationInline]
#admin.site.register(SeatGroup, SeatGroupAdmin)

#class TicketInline(admin.StackedInline):
#    model = Ticket

class SeatGroupPriceInline(admin.StackedInline):
    model = SeatGroupPrice
    extra = 0

class EventDateInline(admin.StackedInline):
    model = EventDate
    extra = 0

class AnnouncementInline(admin.StackedInline):
    model = Announcement
    extra = 0
    max_num = 1

class EventInline(admin.StackedInline):
    model = Event
    extra = 0
    max_num = 1

class TicketInline(admin.StackedInline):
    model = Ticket
    extra = 0
    max_num = 1

class NewsletterAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'content_html':
            result = super(NewsletterAdmin, self).formfield_for_dbfield(db_field, **kwargs)
            result.widget = TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            )
            return result
        return super(NewsletterAdmin, self).formfield_for_dbfield(db_field, **kwargs)
admin.site.register(Newsletter, NewsletterAdmin)

class EventAdmin(admin.ModelAdmin):
    inlines = [EventDateInline, SeatGroupPriceInline, AnnouncementInline]
    readonly_fields = ('product',)
admin.site.register(Event, EventAdmin)

class AnnouncementAdmin(admin.ModelAdmin):
    pass
admin.site.register(Announcement, AnnouncementAdmin)

class TinyMCEFlatPageAdmin(FlatPageAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, TinyMCEFlatPageAdmin)


class TypeOfProductListFilter(SimpleListFilter):
    title = _('Type of product')

    parameter_name = 'type'

    def lookups(self, request, model_admin):
        return (
            ('event', _('Event')),
            ('ticket', _('Ticket')),
            (None, _('Other')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'event':
            return queryset.filter(event__product__isnull=False)
        elif self.value() == 'ticket':
            return queryset.filter(ticket__product__isnull=False)
        elif self.value() == None:
            return queryset.filter(ticket__product__isnull=True, event__product__isnull=True)

        return queryset
    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


class TinyMCEProductOptions(ProductOptions):
    list_filter = ('category', 'date_added','active','featured')
    list_filter += (TypeOfProductListFilter,)
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'description':
            result = super(TinyMCEProductOptions, self).formfield_for_dbfield(db_field, **kwargs)
            result.widget = TinyMCE(
                attrs={'cols': 80, 'rows': 30},
            )
            return result
        return super(TinyMCEProductOptions, self).formfield_for_dbfield(db_field, **kwargs)

admin.site.unregister(Product)
TinyMCEProductOptions.inlines.append(EventInline)
TinyMCEProductOptions.inlines.append(TicketInline)
admin.site.register(Product, TinyMCEProductOptions)
