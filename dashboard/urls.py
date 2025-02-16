from django.urls import path
from .views import dashboard_view, get_filtered_data

urlpatterns = [
    path('', dashboard_view, name='dashboard_2'),
    path('get_filtered_data2/', get_filtered_data, name='get_filtered_data_2'),
]