from django import forms
from django.core.validators import MinValueValidator


class SearchFlightForm(forms.Form):
    start_location = forms.CharField(
        max_length=255,
        error_messages={'required': 'The Form field is required.'}
    )
    end_location = forms.CharField(
        max_length=255,
        error_messages={'required': 'The To field is required.'}
    )
    start_date = forms.DateField(error_messages={'required': 'The Start Date field is required.'})
    passenger_number = forms.IntegerField(
        validators=[MinValueValidator(1)],
        error_messages={'required': 'The Number of Passengers field is required.'}
    )
