from django.contrib import admin
from django.urls import include, path
#from django.views.decorators.csrf import csrf_failure
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from blog import views as blog_views
from django.urls import path
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.conf import settings
from django.conf.urls.static import static
from pages.views import custom_server_error


handler500 = 'pages.views.custom_server_error'
handler404 = 'pages.views.page_not_found'
handler403 = 'pages.views.permission_denied'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/', CreateView.as_view(
        template_name='registration/registration_form.html',
        form_class=UserCreationForm,
        success_url='/'
    ), name='registration'),
    path('auth/login/', LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('auth/logout/', LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
    path('auth/password_change/', PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/auth/password_change/done/'
    ), name='password_change'),
    path('auth/password_change/done/', PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    path('auth/password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/auth/password_reset/done/'
    ), name='password_reset'),
    path('auth/password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/auth/reset/done/'
    ), name='password_reset_confirm'),
    path('auth/reset/done/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
