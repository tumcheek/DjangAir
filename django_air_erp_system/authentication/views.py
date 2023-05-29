from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from django.contrib.auth.views import LoginView as Login
from django.contrib.auth import login, logout, authenticate

from .forms import RegistrationForm, UserLoginForm
from main import tasks
from main.views import get_mail_subject


def staff_logout_view(request):
    logout(request)
    return redirect('auth:staff-login')


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


class StaffLoginView(View):
    template_name = 'authentication/staff_login.html'

    def get(self, request):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('staff:staff-redirect')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('staff:staff-redirect')
        context = {
            'message': 'Invalid email or password.'
        }

        return render(request, self.template_name, context)
