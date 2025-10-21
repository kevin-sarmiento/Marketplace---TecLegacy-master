from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    # ✅ Imagen con valor por defecto y persistencia
    profile_image = models.ImageField(upload_to='profile_pics/', default='profile_pics/default-avatar.png', blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'

def save(self, *args, **kwargs):
        """Evita borrar la imagen anterior si no se cambia."""
        try:
            old_profile = Profile.objects.get(pk=self.pk)
            # Solo elimina la anterior si el usuario realmente sube una nueva
            if old_profile.profile_image and old_profile.profile_image != self.profile_image:
                if old_profile.profile_image.name != 'profile_pics/default-avatar.png':
                    old_path = old_profile.profile_image.path
                    if os.path.exists(old_path):
                        os.remove(old_path)
        except Profile.DoesNotExist:
            pass
        super().save(*args, **kwargs)
# ✅ Crear perfil automáticamente al crear un usuario nuevo
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ✅ Guardar el perfil solo si ya existe (sin borrar la imagen)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()



# ✅ Señal: crear perfil solo al crear el usuario
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ✅ Señal: guardar perfil sin sobrescribir la imagen
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Solo guarda si el perfil existe, no lo recrea ni reemplaza imagen
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ---------------------------------------------------
# MODELO DE DIRECCIONES
# ---------------------------------------------------
class Address(models.Model):
    """
    Modelo para guardar múltiples direcciones del usuario
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100, help_text="Ej: Casa, Trabajo, Oficina")
    recipient_name = models.CharField(max_length=150, verbose_name="Nombre del destinatario")
    street = models.CharField(max_length=255, verbose_name="Dirección")
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_default = models.BooleanField(default=False, verbose_name="Dirección principal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        unique_together = ('user', 'name')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def save(self, *args, **kwargs):
        # Si esta dirección es la principal, desmarcar otras
        if self.is_default:
            Address.objects.filter(user=self.user).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
