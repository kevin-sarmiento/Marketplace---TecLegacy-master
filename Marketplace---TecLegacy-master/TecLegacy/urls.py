from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('cart/', include('cart.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('', include('products.urls')),  # Página principal en products
]

# 🔧 Servir archivos estáticos y multimedia en desarrollo
if settings.DEBUG:
    # Archivos multimedia (imágenes subidas por usuarios)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # ⚠️ Solo sirve archivos estáticos desde STATICFILES_DIRS, no STATIC_ROOT
    from django.conf import settings
    import os

    # Asegura que se sirvan también los estáticos locales durante el desarrollo
    urlpatterns += static('/static/', document_root=os.path.join(settings.BASE_DIR, 'static'))
