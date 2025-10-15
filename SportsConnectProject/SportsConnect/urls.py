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
from facility import views as facilityViews
from django.conf.urls.static import static
from django.conf import settings
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', reservationViews.home, name='home'),
    path('get_availability_by_date/', reservationViews.get_availability_by_date, name='get_availability_by_date'),
    path('reservate/', reservationViews.reservate, name='reservate'),
    path('delete_reservation/', reservationViews.delete_reservation, name='delete_reservation'),
    path('account/', include('accounts.urls')),
    path('historial/', reservationViews.historial, name='Historial'),
    path('delete_reservation_historial/', reservationViews.delete_reservation_historial, name='delete_reservation_historial'),
    path('adminsite/', facilityViews.adminsite, name='adminsite'),
    path('crearespacio/', facilityViews.crear_espacio, name='crear_espacio'),
    path('restringiracceso/<int:facility_id>/', facilityViews.restringir_acceso, name='restringir_acceso'),
    path('analiticas/', facilityViews.mostrarGraficas, name='analisis'),
    path('editar/<int:reserva_id>/', reservationViews.editarReserva, name='editar'),
    path('eliminar_espacio/<int:facility_id>/', facilityViews.eliminar_espacio, name='eliminar_espacio'),
    path('eliminar_reservacion/<int:reservation_id>/', facilityViews.eliminar_reservacion, name='eliminar_reservacion'),
    path('editar_espacio/<int:facility_id>/', facilityViews.editar_espacio, name='editar_espacio'),
    path('waitlist/add/<int:facility_id>/', reservationViews.add_to_waitlist, name='add_to_waitlist'),
    path('rating/', include('rating.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)