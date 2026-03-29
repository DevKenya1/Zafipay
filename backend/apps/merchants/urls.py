from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.MerchantProfileView.as_view(), name='profile'),
    path('mode/toggle/', views.ToggleModeView.as_view(), name='toggle_mode'),
    path('api-keys/', views.APIKeyListCreateView.as_view(), name='api_keys'),
    path('api-keys/<uuid:pk>/revoke/', views.APIKeyRevokeView.as_view(), name='revoke_key'),
]