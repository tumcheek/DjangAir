from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from .forms import FlightForm
from .models import FlightModel
from .utils import get_flights_info


@require_http_methods(["GET"])
def get_flights(request, start_location, end_location, start_date, passenger_number):
    flights_query = FlightModel.objects.filter(
        start_location=start_location,
        end_location=end_location,
        start_date=start_date
    )
    flights = get_flights_info(flights_query, passenger_number)
    is_flights = False if not flights else True

    context = {
        'flights': flights,
        'is_flights': is_flights
    }
    return render(request, 'main/search_result.html', context)


class IndexView(View):
    template_name = 'main/index.html'

    def get(self, request):
        form = FlightForm()
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = FlightForm(request.POST)
        if form.is_valid():
            query_info = {
                'start_location': form.cleaned_data['start_location'],
                'end_location': form.cleaned_data['end_location'],
                'start_date': form.cleaned_data['start_date'],
                'passenger_number': form.cleaned_data['passenger_number']
            }
            return redirect(reverse('main:search_result', kwargs=query_info))

        context = {
            'form': form
        }
        return render(request, self.template_name, context)
