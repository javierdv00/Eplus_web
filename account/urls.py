from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register_view, activate_account, custom_login_view

urlpatterns = [
    path('login/', custom_login_view, name='login'),
    #path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', LogoutView.as_view(), name='logout'),  # No need for next_page here
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),  # Ensure this line exists
]