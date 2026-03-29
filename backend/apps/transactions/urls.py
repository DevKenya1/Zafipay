from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.InitiatePaymentView.as_view(), name='initiate_payment'),
    path('', views.TransactionListView.as_view(), name='transaction_list'),
    path('<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
]
