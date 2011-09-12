from satchmo_store.shop import signals
from localsite.exceptions import IsReservedOrSoldError

def update_ticket_status(cart=None, product=None, form=None, request=None, **kwargs):
    p_types = product.get_subtypes()

    if 'Ticket' in p_types:
        if product.ticket.status == 'freely':
            product.ticket.status = 'reserved'
            product.ticket.save()
        else:
            raise Exception


def check_ticket_status(sender, cartitem=None, added_quantity=0, **kwargs):
    """Listener which vetoes adding tickets to the cart which are reserved or sold."""

    product = cartitem.product
    p_types = product.get_subtypes()

    if 'Ticket' in p_types:
        if product.ticket.status != 'freely':
            raise IsReservedOrSoldError(product, product.ticket.status)

def start_localsite_listening():
    signals.satchmo_cart_add_verify.connect(check_ticket_status)
    #signals.satchmo_cart_add_complete.connect(update_ticket_status)
