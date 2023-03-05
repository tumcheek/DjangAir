from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .forms import FlightForm


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
