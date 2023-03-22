from django import forms
from django.contrib.auth.forms import AuthenticationForm


class SearchFlightForm(forms.Form):
    start_location = forms.CharField(max_length=255)
    end_location = forms.CharField(max_length=255)
    start_date = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    passenger_number = forms.IntegerField()


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Email', 'id': 'id_username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'id_password',
        }
        )
    )
