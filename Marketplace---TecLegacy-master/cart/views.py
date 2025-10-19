from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
import json
import uuid


def _get_or_create_cart(request):
    """Función auxiliar para obtener o crear un carrito."""
    # Si el usuario está autenticado, busca su carrito
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    # Si no está autenticado, usa la sesión
    else:
        # Asegúrate de que la sesión exista
        if not request.session.session_key:
            request.session.create()

        session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)

    return cart


def cart_detail(request):
    """Vista para mostrar el detalle del carrito."""
    cart = _get_or_create_cart(request)
    cart_items = cart.items.all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    """Añadir un producto al carrito."""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = _get_or_create_cart(request)

    # Si la petición es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        quantity = int(request.GET.get('quantity', 1))

        # Comprueba si el producto ya está en el carrito
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)

        # Devuelve respuesta JSON con información actualizada del carrito
        return JsonResponse({
            'success': True,
            'message': f'{product.name} añadido al carrito',
            'cart_items_count': cart.get_total_items(),
            'cart_total': str(cart.get_total_price())
        })

    # Si la petición no es AJAX
    else:
        quantity = int(request.POST.get('quantity', 1))

        # Comprueba si el producto ya está en el carrito
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f'La cantidad de {product.name} ha sido actualizada en tu carrito')
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            messages.success(request, f'{product.name} ha sido añadido a tu carrito')

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

    # Si el carrito está vacío, redirige a la vista del carrito
    if cart.items.count() == 0:
        messages.info(request, 'Tu carrito está vacío. Añade algunos productos antes de hacer checkout.')
        return redirect('cart:cart_detail')

    # Si es una petición POST, procesa el formulario de pedido
    if request.method == 'POST':
        # Validar que todos los campos necesarios estén presentes
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'country', 'postal_code',
                           'payment_method']

        for field in required_fields:
            if not request.POST.get(field):
                messages.error(request, f'El campo {field} es obligatorio')
                return redirect('cart:checkout')

        # Crear un nuevo pedido
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

        # Crear items del pedido basados en el carrito
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        # Vaciar el carrito
        cart.items.all().delete()

        messages.success(request, '¡Tu pedido ha sido creado correctamente!')
        return redirect('cart:payment_process', order_id=order.id)

    # Prepopular campos con información del perfil si existe
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

    # Si el pago ya está completo, redirigir a la página de éxito
    if order.payment_status == 'completado':
        return redirect('cart:payment_success', order_id=order.id)

    payment_method = order.payment_method

    context = {
        'order': order,
        'payment_method': payment_method,
        'client_id': 'PAYPAL_CLIENT_ID',  # En producción, esto vendría de las variables de entorno
    }

    # Usar el nombre correcto de la plantilla
    return render(request, 'cart/payment_process.html', context)


@login_required
def payment_execute(request, order_id):
    """Vista para ejecutar el pago después de aprobación."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Simular un pago exitoso
        payment_id = request.POST.get('payment_id', '')

        if not payment_id:
            # Generar un ID de pago simulado
            payment_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"

        # Actualizar la orden
        order.payment_status = 'completado'
        order.payment_reference = payment_id
        order.status = 'procesando'  # El estado del pedido pasa a procesando
        order.save()

        messages.success(request, '¡Tu pago se ha procesado correctamente!')
        return redirect('cart:payment_success', order_id=order.id)

    return redirect('cart:payment_process', order_id=order_id)


@login_required
def payment_success(request, order_id):
    """Vista de éxito después del pago."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    context = {
        'order': order,
    }

    # Usar el nombre correcto de la plantilla
    return render(request, 'cart/payment_success.html', context)


@login_required
def payment_cancel(request, order_id):
    """Vista para cancelar el pago."""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Actualizar la orden
    order.payment_status = 'fallido'
    order.save()

    messages.warning(request, 'El pago ha sido cancelado.')
    return redirect('cart:checkout')