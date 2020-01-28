from django.urls import path

from api.views import search_ticket

urlpatterns = [
    path('', search_ticket),
]
