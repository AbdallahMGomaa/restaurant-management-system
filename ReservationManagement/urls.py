from django.urls import path
from ReservationManagement import views

urlpatterns = [
    path('checkAvailableSlots/', views.checkAvailableTimeSlots),
    path('reserve/', views.reserveTimeSlot),
    path('getTodays/', views.getTodaysReservations),
    path('getAll/', views.getAllReservations),
    path('delete/', views.deleteReservation)
]