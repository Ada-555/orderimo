"""Cart context processor — makes cart available in all templates."""

from .models import Cart


def cart(request):
    """Return the current cart dict for template context."""

    if request.user.is_authenticated:
        cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    elif request.session.session_key:
        cart_obj, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    else:
        cart_obj = None

    return {
        "cart": cart_obj,
        "cart_item_count": cart_obj.item_count if cart_obj else 0,
        "cart_grand_total": cart_obj.grand_total if cart_obj else 0,
    }
