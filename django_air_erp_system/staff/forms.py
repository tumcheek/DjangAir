from django import forms


class BoardRegistrationForm(forms.Form):
    ticket_number = forms.IntegerField()


class StaffRegistrationForm(forms.Form):
    OPTIONS = [
        ('gate_managers', 'Gate managers'),
        ('supervisors', 'Supervisors'),
    ]

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
    group = forms.ChoiceField(
        choices=OPTIONS,
        widget=forms.RadioSelect(
            attrs={'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'}
        ),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Password', 'class': 'col-xl-3 col-lg-8 col-sm-12 mb-3 p-3'}
        ),
    )
