from django.contrib import admin
from store.localsite.models import *

class SeatLocationInline(admin.TabularInline):
    model = SeatLocation

class HallSchemeAdmin(admin.ModelAdmin):
    inlines = [SeatLocationInline,]
admin.site.register(HallScheme, HallSchemeAdmin)

class HallAdmin(admin.ModelAdmin):
    pass
admin.site.register(Hall, HallAdmin)

class TicketAdmin(admin.ModelAdmin):
    pass
admin.site.register(Ticket, TicketAdmin)

#class TicketInline(admin.StackedInline):
#    model = Ticket

class EventDateInline(admin.StackedInline):
    model = EventDate

class EventAdmin(admin.ModelAdmin):
    inlines = [EventDateInline, ]
admin.site.register(Event, EventAdmin)
