from django.urls import path
from .import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(
        'result/<str:start_location>/<str:end_location>/<str:start_date>/<int:passenger_number>/',
        views.get_flights,
        name='search_result'
    ),
]
