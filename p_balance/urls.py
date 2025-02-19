from django.urls import path
from .views import dash_home_view, dashboard_view, get_filtered_data

urlpatterns = [
    path('', dash_home_view, name='dash_home'),
    path('dashboard/building/', dashboard_view, {'dash_model': 'Building'}, name='dashboard_building'),
    path('dashboard/ambientes/', dashboard_view, {'dash_model': 'Ambientes'}, name='dashboard_ambientes'),
    path('get_filtered_data/<str:dash_model>/', get_filtered_data, name='get_filtered_data'),  # Pass model
]