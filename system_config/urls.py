from django.urls import path
from . import views

app_name = 'system_config'

urlpatterns = [
    path('configuration/', views.configuration_home, name='configuration_home'),
    path('configuration/societe/', views.company_settings_view, name='company_settings'),
    path('configuration/listes/<slug:slug>/', views.list_generic, name='list_generic'),
    path('configuration/parametres/', views.parameters_view, name='parameters'),
    path('configuration/parametres/test-email/', views.test_email_settings, name='test_email'),
]
