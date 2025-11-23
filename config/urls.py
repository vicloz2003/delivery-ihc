from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users
    path('api/users/', include('core.urls')),  # ← CAMBIAR DE 'api/auth/' a 'api/users/'
    
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/', include('payments.urls')),

    # Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]