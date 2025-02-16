from django.urls import path
from .views import dashboard_view, get_filtered_data

urlpatterns = [
    # path('', select_data, name='p_balance'),
    # path('dashboard', dashboard_view, name='dashboard'),
    path('', dashboard_view, name='p_balance'),
    path('get_filtered_data/', get_filtered_data, name='get_filtered_data'),
]