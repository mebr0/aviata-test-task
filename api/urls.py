from django.urls import path

from api.views import get_ticket

urlpatterns = [
    path('', get_ticket),
]
