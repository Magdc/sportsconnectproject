"""
URL configuration for SportsConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from reservation import views as reservationViews

from django.conf.urls.static import static
from django.conf import settings
from reservation import views
from django.urls import path, include
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',reservationViews.home, name='home'),
    path('get_availability_by_date/', reservationViews.get_availability_by_date, name='get_availability_by_date'),
    path('reservate/', reservationViews.reservate, name='reservate'),
    path('delete_reservation/', reservationViews.delete_reservation, name='delete_reservation'),
    path('account/', include('accounts.urls')),
    path('historial/', reservationViews.historial, name='Historial'),
    path('delete_reservation_historial/', views.delete_reservation_historial, name='delete_reservation_historial'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)