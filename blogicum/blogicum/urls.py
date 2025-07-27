from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from blog.views import SignUpView


handler403 = 'pages.views.permission_denied_view'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        SignUpView.as_view(),
        name='registration',
    ),
    path('pages/', include('pages.urls', namespace='pages')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
