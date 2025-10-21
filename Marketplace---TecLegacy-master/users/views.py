from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AddressForm
from .models import Profile, Address
from cart.models import Order  # ✅ Importamos los pedidos
from products.models import Product, Category


def register(request):
    """Vista para registro de nuevos usuarios."""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada para {username}! Ahora puedes iniciar sesión.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    """Vista principal del perfil de usuario: datos, direcciones y pedidos."""
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)  # 🔧 asegura que el perfil exista

    # ✅ Manejo de formularios POST (datos e imagen)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            # 🔧 Asegura que se guarde la imagen y persista
            updated_profile = profile_form.save(commit=False)
            if not updated_profile.profile_image:
                updated_profile.profile_image = 'profile_pics/default-avatar.png'
            updated_profile.save()

            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Error al actualizar el perfil. Revisa los datos ingresados.')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    # ✅ Direcciones del usuario
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    address_form = AddressForm()

    # ✅ Categorías para el navbar
    categories = Category.objects.filter(is_active=True)

    # ✅ Pedidos del usuario
    orders = Order.objects.filter(user=user).order_by('-created_at')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'addresses': addresses,
        'address_form': address_form,
        'categories': categories,
        'orders': orders,
    }
    return render(request, 'users/profile.html', context)



# 🔧 CORRECCIÓN: esta función ahora permite editar o crear direcciones
@login_required
@require_http_methods(["POST"])
def add_address(request):
    """Agrega o actualiza una dirección según si viene un ID en el formulario."""
    address_id = request.POST.get("address_id")

    if address_id:  # 🔧 EDITAR
        address = get_object_or_404(Address, id=address_id, user=request.user)
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Dirección actualizada correctamente!")
        else:
            messages.error(request, "Error al actualizar la dirección.")
    else:  # ➕ CREAR NUEVA
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            try:
                address.save()
                messages.success(request, "¡Dirección agregada correctamente!")
            except Exception:
                messages.error(request, "Ya existe una dirección con ese nombre.")
        else:
            messages.error(request, "Error al agregar la dirección.")

    return redirect("users:profile")


@login_required
@require_http_methods(["POST"])
def edit_address(request, address_id):
    """Editar una dirección existente."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    form = AddressForm(request.POST, instance=address)
    if form.is_valid():
        form.save()
        messages.success(request, '¡Dirección actualizada correctamente!')
    else:
        messages.error(request, 'Error al actualizar la dirección.')
    return redirect('users:profile')


@login_required
@require_http_methods(["POST"])
def delete_address(request, address_id):
    """Eliminar una dirección."""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, '¡Dirección eliminada correctamente!')
    return redirect('users:profile')


@login_required
def order_history(request):
    """Vista independiente para historial de pedidos."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/order_history.html', {'orders': orders})


def logout_view(request):
    """Cerrar sesión del usuario y redirigir al inicio."""
    logout(request)
    return redirect('products:index')


# 🟨 FUNCIONES VIEJAS ACTUALIZADAS A "users:profile"
@login_required
def agregar_direccion(request):
    """Agregar nueva dirección al perfil (versión antigua)."""
    if request.method == 'POST':
        direccion = Direccion.objects.create(
            usuario=request.user,
            nombre_direccion=request.POST.get('nombre_direccion', ''),
            nombre_destinatario=request.POST.get('nombre_destinatario', ''),
            direccion=request.POST.get('direccion', ''),
            ciudad=request.POST.get('ciudad', ''),
            codigo_postal=request.POST.get('codigo_postal', ''),
            pais=request.POST.get('pais', ''),
            telefono=request.POST.get('telefono', ''),
            es_principal=request.POST.get('es_principal') == 'on'
        )
        messages.success(request, 'Dirección agregada exitosamente')
        return redirect('users:profile')

    return redirect('users:profile')


@login_required
def editar_direccion(request, direccion_id):
    """Editar una dirección existente (versión antigua)."""
    direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)

    if request.method == 'POST':
        direccion.nombre_direccion = request.POST.get('nombre_direccion', direccion.nombre_direccion)
        direccion.nombre_destinatario = request.POST.get('nombre_destinatario', direccion.nombre_destinatario)
        direccion.direccion = request.POST.get('direccion', direccion.direccion)
        direccion.ciudad = request.POST.get('ciudad', direccion.ciudad)
        direccion.codigo_postal = request.POST.get('codigo_postal', direccion.codigo_postal)
        direccion.pais = request.POST.get('pais', direccion.pais)
        direccion.telefono = request.POST.get('telefono', '')
        direccion.es_principal = request.POST.get('es_principal') == 'on'

        direccion.save()
        messages.success(request, 'Dirección actualizada exitosamente')
        return redirect('users:profile')

    return redirect('users:profile')


@login_required
def eliminar_direccion(request, direccion_id):
    """Eliminar dirección del perfil (versión antigua)."""
    if request.method == 'POST':
        direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
        direccion.delete()
        messages.success(request, 'Dirección eliminada exitosamente')
        return redirect('users:profile')

    return redirect('users:profile')


@login_required
def establecer_principal(request, direccion_id):
    """Establecer una dirección como principal (versión antigua)."""
    if request.method == 'POST':
        direccion = get_object_or_404(Direccion, id=direccion_id, usuario=request.user)
        direccion.es_principal = True
        direccion.save()
        messages.success(request, 'Dirección establecida como principal')
        return redirect('users:profile')

    return redirect('users:profile')
def clean_is_default(self):
    is_default = self.cleaned_data.get('is_default')
    user = self.instance.user if self.instance.pk else self.initial.get('user')
    if is_default and Address.objects.filter(user=user, is_default=True).exclude(pk=self.instance.pk).exists():
        raise forms.ValidationError("Ya tienes una dirección principal.")
    return is_default
