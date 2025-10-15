import os
from typing import Optional, Callable
from .notification_services import ConsoleNotificationService, EmailNotificationService, NotificationService

# Factory: centraliza la creación del servicio de notificaciones
# Permite seleccionar la "estrategia" (Strategy) adecuada según entorno/configuración

def get_notification_service(email_sender: Optional[Callable[[str, str, str], str]] = None) -> NotificationService:
    """
    Crea y devuelve una implementación de NotificationService.
    - Si la variable de entorno USE_EMAIL_NOTIFICATIONS es 'true' (case-insensitive) y se provee email_sender,
      retorna EmailNotificationService.
    - En cualquier otro caso retorna ConsoleNotificationService.

    email_sender: función callable con firma (user_email, subject, message) -> str
    """
    use_email = os.getenv('USE_EMAIL_NOTIFICATIONS', 'false').lower() == 'true'

    if use_email and email_sender is not None:
        return EmailNotificationService(email_sender)

    return ConsoleNotificationService()
