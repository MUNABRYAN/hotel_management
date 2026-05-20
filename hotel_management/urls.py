from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('usuarios.urls')),
    path('', RedirectView.as_view(pattern_name='hotel:dashboard', permanent=False)),
    path('hotel/', include('hotel.urls')),
    path('restaurant/', include('restaurant.urls')),
    path('configuracion/', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# URLs para probar paginas de error en desarrollo
from django.views.defaults import page_not_found, server_error

urlpatterns += [
    path('404/', page_not_found, {'exception': Exception('Pagina no encontrada')}),
    path('500/', server_error),
]