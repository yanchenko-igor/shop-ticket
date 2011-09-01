from django.contrib import admin
from store.localsite.models import *

class SeatGroupInline(admin.TabularInline):
    model = SeatGroup
    extra = 0

class SeatLocationInline(admin.TabularInline):
    model = SeatLocation
    extra = 0

class HallSchemeAdmin(admin.ModelAdmin):
    inlines = [SeatGroupInline,]
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

class SeatGroupAdmin(admin.ModelAdmin):
    inlines = [SeatLocationInline]
admin.site.register(SeatGroup, SeatGroupAdmin)

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

class EventAdmin(admin.ModelAdmin):
    inlines = [EventDateInline, SeatGroupPriceInline, AnnouncementInline]
    readonly_fields = ('product',)
admin.site.register(Event, EventAdmin)

class AnnouncementAdmin(admin.ModelAdmin):
    pass
admin.site.register(Announcement, AnnouncementAdmin)
