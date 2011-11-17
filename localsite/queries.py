from keyedcache import cache_get, cache_set, NotCachedError
from product.models import Product
from localsite.models import Event


def bestsellers(count):
    return Product.objects.filter(id__in=Event.objects.active().extra(select={'s':'select count(*) from localsite_ticket join shop_orderitem on(localsite_ticket.product_id=shop_orderitem.product_id) where localsite_ticket.event_id = localsite_event.product_id'}).order_by('-s'))[:count]
