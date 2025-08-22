from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    """Custom login view using email authentication"""
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'You have been logged in successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    next_page = reverse_lazy('core:landing_page')
    template_name = None  # Don't render a template, just redirect

    def get(self, request, *args, **kwargs):
        """Handle GET requests for logout"""
        messages.success(request, 'You have been logged out successfully.')
        return self.logout(request)

    def post(self, request, *args, **kwargs):
        """Handle POST requests for logout"""
        messages.success(request, 'You have been logged out successfully.')
        return self.logout(request)

    def logout(self, request):
        """Perform the actual logout"""
        from django.contrib.auth import logout
        logout(request)
        return redirect(self.next_page)


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            f'Account created successfully for {user.email}. You can now log in.'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required
def profile_view(request):
    """View user profile"""
    context = {
        'user': request.user,
        'title': 'My Profile'
    }
    return render(request, 'accounts/profile_view.html', context)


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    """Edit user profile view"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


# Keep the old ProfileView for backward compatibility
@method_decorator(login_required, name='dispatch')
class ProfileView(UpdateView):
    """User profile view (legacy)"""
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required
def dashboard(request):
    """Dashboard view for authenticated users"""
    context = {
        'user': request.user,
        'title': 'Dashboard'
    }
    return render(request, 'accounts/dashboard.html', context)


def register_view(request):
    """Function-based registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Account created successfully for {user.email}. You can now log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Function-based login view"""
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have been logged in successfully.')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Function-based logout view that handles all request methods"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing_page')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view that provides better user feedback"""
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        """Process the form and provide appropriate feedback"""
        email = form.cleaned_data['email']
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
            # User exists, proceed with normal password reset
            messages.success(
                self.request,
                f'Password reset instructions have been sent to {email}. '
                'Please check your inbox and spam folder.'
            )
            return super().form_valid(form)
        except User.DoesNotExist:
            # User doesn't exist, provide helpful message
            messages.info(
                self.request,
                f'No account found with email {email}. '
                'Please check your email address or register for a new account.'
            )
            # Still redirect to done page but with different message
            return redirect(self.success_url)
    
    def form_invalid(self, form):
        """Handle form errors"""
        messages.error(self.request, 'Please enter a valid email address.')
        return super().form_invalid(form)
