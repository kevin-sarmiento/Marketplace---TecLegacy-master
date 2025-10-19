from .models import Cart, CartItem


def cart_processor(request):
    """Contexto que proporciona información del carrito en todas las plantillas."""
    cart_items_count = 0
    cart_total = 0

    # Si el usuario está autenticado, busca su carrito
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items_count = cart.get_total_items()
            cart_total = cart.get_total_price()
        except Cart.DoesNotExist:
            pass
    # Si no está autenticado, busca el carrito por session_id
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_id=session_key)
                cart_items_count = cart.get_total_items()
                cart_total = cart.get_total_price()
            except Cart.DoesNotExist:
                pass

    return {
        'cart_items_count': cart_items_count,
        'cart_total': cart_total
    }