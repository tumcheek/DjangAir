from django import forms


class FlightForm(forms.Form):
    start_location = forms.CharField(max_length=255)
    end_location = forms.CharField(max_length=255)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    passenger_number = forms.IntegerField()
