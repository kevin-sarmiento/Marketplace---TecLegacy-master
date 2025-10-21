from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Address


# -------------------------------------------------
# FORMULARIO DE REGISTRO DE USUARIO
# -------------------------------------------------
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# -------------------------------------------------
# FORMULARIO DE ACTUALIZACIÓN DE USUARIO
# -------------------------------------------------
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


# -------------------------------------------------
# FORMULARIO DE PERFIL
# -------------------------------------------------
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'country', 'postal_code', 'profile_image']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'País'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código postal'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control', 'hidden': True}),
        }


# -------------------------------------------------
# FORMULARIO DE DIRECCIONES (UNIFICADO)
# -------------------------------------------------
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'name', 'recipient_name', 'street', 'city',
            'postal_code', 'country', 'phone', 'is_default'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Casa, Trabajo...'
            }),
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección completa'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ciudad'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código postal'
            }),
            'country': forms.Select(choices=[
                ('', 'Selecciona un país'),
                ('España', 'España'),
                ('Colombia', 'Colombia'),
                ('Francia', 'Francia'),
                ('Italia', 'Italia'),
                ('Alemania', 'Alemania'),
                ('Otro', 'Otro'),
            ], attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono'
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
