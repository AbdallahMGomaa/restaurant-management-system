from django.urls import path
from UserManagement import views


urlpatterns = [
    path('signup/',views.createUser),
    path('login/',views.login),
    path('delete/',views.deleteUser),
    path('getAll/',views.getUsers)
]