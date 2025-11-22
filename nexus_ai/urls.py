from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/en/', permanent=False)),
    path('i18n/setlang/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('core.urls')),
    prefix_default_language=True,
)
