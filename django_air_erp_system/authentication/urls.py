from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
        path('login/', views.LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('registration/', views.RegistrationView.as_view(), name='registration'),
        path('staff/login/', views.StaffLoginView.as_view(), name='staff-login'),
        path('staff/logout/', views.staff_logout_view, name='staff-logout'),
]
