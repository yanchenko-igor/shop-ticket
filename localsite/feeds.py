from django.contrib.syndication.views import Feed
from localsite.models import Event

class EventFeed(Feed):
    title = "site news"
    link = "/sitenews/"
    description = "description"

    def items(self):
        return Event.objects.order_by('-min_date')[:25]

    def item_title(self, item):
        return item.product.name

    def item_description(self, item):
        return item.product.description
