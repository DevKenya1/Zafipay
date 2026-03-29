from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/merchants/', include('apps.merchants.urls')),
    path('api/v1/transactions/', include('apps.transactions.urls')),
    path('api/v1/providers/', include('apps.providers.urls')),
    path('api/v1/webhooks/', include('apps.webhooks.urls')),
    path('api/v1/refunds/', include('apps.refunds.urls')),
]
