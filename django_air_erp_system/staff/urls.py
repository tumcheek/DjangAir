from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .import views

app_name = 'staff'

urlpatterns = [
    path('redirect/', views.staff_redirect_view, name='staff-redirect'),
    path('gate-manager/', views.GateManagerView.as_view(), name='gate-manager'),
    path('check-in-manager/', views.CheckInManagerView.as_view(), name='check-in-manager'),
    path('supervisor/', views.SupervisorView.as_view(), name='supervisor'),
    path('flights/', views.get_future_flights, name='flights'),
    path('flights/board_registration/<slug:flight_slug>/', views.BoardRegistrationView.as_view(), name='board-registration')
]
