from django.urls import path
from .import views

app_name = 'main'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path(
        'search/result/<str:start_location>/<str:end_location>/<str:start_date>/<int:passenger_number>/',
        views.get_flights,
        name='search_result'
    ),
    path(
        'booking/<slug:slug_info>/<str:start_date>/<int:passenger_number>/',
        views.BookView.as_view(),
        name='book_ticket'
    )
]
