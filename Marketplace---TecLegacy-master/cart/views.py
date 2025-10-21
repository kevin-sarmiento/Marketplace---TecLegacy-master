from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
import json
import uuid
from products.models import Product, Category


def _get_or_create_cart(request):
    """Función auxiliar para obtener o crear un carrito."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart


def cart_detail(request):
    """Vista para mostrar el detalle del carrito."""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()
    categories = Category.objects.filter(is_active=True)

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'categories': categories
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    """Añadir un producto al carrito (AJAX o normal)"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = _get_or_create_cart(request)

    color_id = request.POST.get('color') or request.GET.get('color')
    size_id = request.POST.get('size') or request.GET.get('size')
    quantity = int(request.POST.get('quantity', 1))

    color = None
    size = None

    if color_id:
        from products.models import Color
        color = Color.objects.filter(id=color_id).first()

    if size_id:
        from products.models import Size
        size = Size.objects.filter(id=size_id).first()

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color=color,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'{product.name} agregado al carrito',
            'cart_items_count': cart.get_total_items(),
            'cart_total': str(cart.get_total_price())
        })

    return redirect('cart:cart_detail')


def update_cart(request):
    """Actualizar cantidades en el carrito."""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        action = data.get('action')

        cart_item = get_object_or_404(CartItem, id=item_id)

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                cart_item.delete()
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'cart_total': str(cart_item.cart.get_total_price()),
                    'cart_items_count': cart_item.cart.get_total_items()
                })
        elif action == 'remove':
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'removed': True,
                'cart_total': str(cart_item.cart.get_total_price()),
                'cart_items_count': cart_item.cart.get_total_items()
            })

        cart_item.save()

        return JsonResponse({
            'success': True,
            'item_total': str(cart_item.get_cost()),
            'quantity': cart_item.quantity,
            'cart_total': str(cart_item.cart.get_total_price()),
            'cart_items_count': cart_item.cart.get_total_items()
        })

    return JsonResponse({'success': False})


@login_required
def checkout(request):
    """Vista para el proceso de checkout."""
    cart = _get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.info(request, 'Tu carrito está vacío. Añade algunos productos antes de hacer checkout.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        required_fields = [
            'first_name', 'last_name', 'email', 'phone',
            'address', 'city', 'country', 'postal_code', 'payment_method'
        ]

        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f'El campo {field} es obligatorio')
                return redirect('cart:checkout')

        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            postal_code=request.POST.get('postal_code'),
            total_paid=cart.get_total_price(),
            payment_method=request.POST.get('payment_method')
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        cart.items.all().delete()
        messages.success(request, '¡Tu pedido ha sido creado correctamente!')
        return redirect('cart:payment_process', order_id=order.id)

    initial_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'address': profile.address,
            'city': profile.city,
            'country': profile.country,
            'postal_code': profile.postal_code
        }

    context = {
        'cart': cart,
        'initial_data': initial_data
    }
    return render(request, 'cart/checkout.html', context)


@login_required
def payment_process(request, order_id):
    """Vista para procesar el pago de una orden."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'completado':
        return redirect('cart:payment_success', order_id=order.id)

    payment_method = order.payment_method
    context = {
        'order': order,
        'payment_method': payment_method,
        'client_id': 'PAYPAL_CLIENT_ID',
    }
    return render(request, 'cart/payment_process.html', context)


@login_required
def payment_execute(request, order_id):
    """Vista para ejecutar el pago después de aprobación."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)

        payment_id = request.POST.get('payment_id', '')
        if not payment_id:
            payment_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"

        order.payment_status = 'completado'
        order.payment_reference = payment_id
        order.status = 'procesando'
        order.save()

        messages.success(request, '¡Tu pago se ha procesado correctamente!')
        return redirect('cart:payment_success', order_id=order.id)

    return redirect('cart:payment_process', order_id=order_id)


@login_required
def payment_success(request, order_id):
    """Vista de éxito después del pago."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'cart/payment_success.html', context)


@login_required
def payment_cancel(request, order_id):
    """Vista para cancelar el pago."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.payment_status = 'fallido'
    order.save()

    messages.warning(request, 'El pago ha sido cancelado.')
    return redirect('cart:checkout')
