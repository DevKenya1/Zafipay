from django.urls import path
from . import views

urlpatterns = [
    path('', views.RefundListView.as_view(), name='refund_list'),
    path('initiate/', views.InitiateRefundView.as_view(), name='initiate_refund'),
    path('<uuid:pk>/', views.RefundDetailView.as_view(), name='refund_detail'),
]
