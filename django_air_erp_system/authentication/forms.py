from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import PassengerModel


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(
        widget=forms.TextInput(
            attrs=
            {
                'class': 'col-xl-3 col-lg-8 col-sm-12 p-3',
                'placeholder': 'Email',
                'id': 'id_username'
            }
        )
    )
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 mt-3 p-3',
            'placeholder': 'Password',
            'id': 'id_password',
        }
        )
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'autocomplete': 'email',
                'placeholder': 'Email',
                'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'
            }
        )
    )

    first_name = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={'placeholder': 'First name', 'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'}))
    last_name = forms.CharField(
        max_length=254,
        widget=forms.TextInput(
            attrs={'placeholder': 'Last name', 'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'}))

    def __init__(self, *args, **kwargs):

        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].widget.attrs['class'] = 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
        self.fields['password2'].widget.attrs['class'] = 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'

    class Meta:
        model = PassengerModel
        fields = ('email', 'first_name', 'last_name')
