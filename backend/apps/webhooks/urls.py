from django.urls import path
from . import views

urlpatterns = [
    path('endpoints/', views.WebhookEndpointListCreateView.as_view(), name='webhook_endpoints'),
    path('endpoints/<uuid:pk>/', views.WebhookEndpointDetailView.as_view(), name='webhook_endpoint_detail'),
    path('deliveries/', views.WebhookDeliveryListView.as_view(), name='webhook_deliveries'),
    path('deliveries/<uuid:pk>/retry/', views.WebhookDeliveryRetryView.as_view(), name='webhook_retry'),
]
