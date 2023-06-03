from django import forms


class BoardRegistrationForm(forms.Form):
    ticket_number = forms.IntegerField()
