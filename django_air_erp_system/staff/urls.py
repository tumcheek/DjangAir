from django.contrib.auth.decorators import login_required
from django.urls import path, include
from .import views

app_name = 'staff'

urlpatterns = [
    path('redirect/', views.staff_redirect_view, name='staff-redirect'),
    path('gate-manager/', views.GateManagerView.as_view(), name='gate-manager'),
    path('supervisor/', views.SupervisorView.as_view(), name='supervisor'),
    path('<str:group>/flights/', views.get_future_flights, name='flights'),
    path('<str:group>/staff-registration/', views.StaffRegistrationView.as_view(), name='staff-registration'),
    path('<str:group>/flights/<slug:flight_slug>/cancel', views.cancel_flights, name='cancel-flight'),
    path('<str:group>/flights/<slug:flight_slug>/uncancel', views.uncancel_flights, name='uncancel-flight'),
    path('flights/board_registration/<slug:flight_slug>/', views.BoardRegistrationView.as_view(), name='board-registration')
]
