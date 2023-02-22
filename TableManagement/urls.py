from django.urls import path
from TableManagement import views

urlpatterns = [
    path('get/',views.getTables),
    path('delete/',views.deleteTable),
    path('add/',views.addTable)
]