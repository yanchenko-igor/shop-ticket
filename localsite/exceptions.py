from satchmo_store.shop.exceptions import CartAddProhibited
from django.utils.translation import ugettext as _

class IsReservedOrSoldError(CartAddProhibited):

    def __init__(self, product, status):
        if status == 'reserved':
            msg = _("'%s' is reserved.") % product.translated_name()
        elif status == 'sold':
            msg = _("'%s' is sold.") % product.translated_name()

        CartAddProhibited.__init__(self, product, msg)
        self.status = status
