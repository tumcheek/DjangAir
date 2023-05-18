from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.views import LoginView as Login

from .forms import RegistrationForm, UserLoginForm
from main import tasks
from main.views import get_mail_subject


class LoginView(Login):
    """
    View that handles user authentication and login.

    If the user is already authenticated, redirects them to the success URL.

    Parameters:
        template_name (str): The name of the template to use for rendering the login page.
        redirect_authenticated_user (bool): Whether to redirect authenticated users to the success URL.
        authentication_form (class): The form to use for authenticating the user.

    Returns:
        HTTP response: A redirect to the success URL or a rendered login page.
    """
    template_name = 'authentication/login.html'
    redirect_authenticated_user = True
    authentication_form = UserLoginForm


class RegistrationView(View):
    """A view for registering a new user."""
    template_name = 'authentication/registration.html'

    def get(self, request) -> HttpResponse:
        """Render the registration form."""
        form = RegistrationForm()
        context = {
            'form': form
        }

        return render(request, self.template_name, context)

    def post(self, request) -> HttpResponse:
        """Process the registration form."""
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            message = render_to_string(
                'authentication/email_messages/user_registration_message.html',
            )
            registration_mail_subject = get_mail_subject('registration', 'Registration')
            tasks.send_mail_task.delay(message, email, registration_mail_subject)

            return redirect('main:cabinet')

        context = {
            'form': form
        }
        return render(request, self.template_name, context)
