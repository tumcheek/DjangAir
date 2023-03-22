from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path, include
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
    ),

    path(
        'booking/<slug:slug_info>/<str:start_date>/<int:passenger_number>/<str:error>',
        views.BookView.as_view(),
        name='book_ticket_error'
    ),
    path('payment/',
         include([
             path('success/',
                  views.SuccessPayment.as_view(),
                  name='success_payment'
                  ),
             path('cancel/',
                  views.CancelPayment.as_view(),
                  name='cancel_payment'
                  ),
             path('<str:name>/<int:total>/<int:amount>/',
                  views.PaymentView.as_view(),
                  name='payment'
                  ),
                ]
            )
         ),
    path('auth/', include([
        path('login/', views.LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
    ])),
]
