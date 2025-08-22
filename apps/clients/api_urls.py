from django.urls import path
from . import api_views

app_name = 'clients_api'

urlpatterns = [
    path('<int:client_id>/', api_views.client_detail_api, name='client_detail'),
]
