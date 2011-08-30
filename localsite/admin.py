from django.contrib import admin
from store.localsite.models import *

class SeatGroupInline(admin.TabularInline):
    model = SeatGroup

class SeatLocationInline(admin.TabularInline):
    model = SeatLocation

class HallSchemeAdmin(admin.ModelAdmin):
    inlines = [SeatLocationInline,SeatGroupInline]
admin.site.register(HallScheme, HallSchemeAdmin)

class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
admin.site.register(City, CityAdmin)

class HallAdmin(admin.ModelAdmin):
    pass
admin.site.register(Hall, HallAdmin)

class TicketAdmin(admin.ModelAdmin):
    pass
admin.site.register(Ticket, TicketAdmin)

#class TicketInline(admin.StackedInline):
#    model = Ticket

class SeatGroupPriceInline(admin.StackedInline):
    model = SeatGroupPrice

class EventDateInline(admin.StackedInline):
    model = EventDate

class EventAdmin(admin.ModelAdmin):
    inlines = [EventDateInline, SeatGroupPriceInline]
admin.site.register(Event, EventAdmin)

class AnnouncementAdmin(admin.ModelAdmin):
    pass
admin.site.register(Announcement, AnnouncementAdmin)
