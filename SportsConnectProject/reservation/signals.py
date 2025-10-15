from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Reservation, WaitList
from .notification_factory import get_notification_service
from .views import send_email

@receiver(post_delete, sender=Reservation)
def notify_waitlist_on_cancellation(sender, instance: Reservation, **kwargs):
    """
    Observer pattern via Django signals: cuando se elimina una Reserva, se notifica a los usuarios
    en la lista de espera para la misma instalación y fecha.
    """
    facility = instance.facilities
    date = instance.availability.date

    # Obtener usuarios en lista de espera para esa instalación y fecha, priorizando por fecha de solicitud
    waiters = WaitList.objects.for_facility_on_date(facility, date)

    if not waiters:
        return

    service = get_notification_service(email_sender=send_email)
    subject = f"Cupo disponible en {facility.name}"
    message = (
        f"Se ha liberado un cupo para {facility.name} el {date}.\n"
        f"Ingresa al sistema para realizar tu reserva."
    )

    for waiter in waiters:
        user_email = getattr(waiter.user, 'email', None)
        if user_email:
            service.send(user_email, subject, message)