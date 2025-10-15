# Patrones de Diseño en Python aplicados

Este documento describe los patrones de diseño de Python aplicados en el proyecto y la justificación detrás de su elección.

## Strategy (Estrategia) en Notificaciones
- "Estrategia" permite definir una familia de algoritmos, encapsularlos e intercambiarlos dinámicamente.
- En `reservation/notification_services.py` definimos la abstracción `NotificationService` y dos estrategias concretas:
  - `ConsoleNotificationService`: imprime la notificación en consola (ideal para desarrollo/pruebas).
  - `EmailNotificationService`: delega el envío a una función `email_sender` (en este caso `send_email`).
- Beneficios:
  - Desacopla el código de alto nivel de la implementación concreta de notificaciones.
  - Facilita pruebas (inyectar una estrategia mock) y futuras extensiones (SMS, Push, etc.).

## Factory (Fábrica) para Selección de Estrategia
- Se incorporó `reservation/notification_factory.py` con la función `get_notification_service(...)`.
- Esta fábrica centraliza la creación del servicio de notificaciones y selecciona la estrategia adecuada según configuración (variable de entorno `USE_EMAIL_NOTIFICATIONS`).
- Beneficios:
  - Punto único de decisión para la construcción de estrategias.
  - Aplicación del principio Open/Closed: agregar un nuevo canal implica registrar una nueva estrategia, sin modificar clientes.

## Uso en las Vistas
- En `reservation/views.py`, las funciones `reserva_confirmacion` y `WaitList_confirmacion` usan la fábrica cuando no se inyecta explícitamente un servicio.
- Esto permite que, según el entorno, el sistema envíe emails reales o simplemente loguee en consola.

### Ejemplos
```python
from reservation.notification_factory import get_notification_service
from reservation.notification_services import ConsoleNotificationService, EmailNotificationService

# Por defecto (según entorno):
service = get_notification_service(email_sender=send_email)
service.send(user_email, subject, message)

# Forzar consola (útil en pruebas):
service = ConsoleNotificationService()

# Forzar email (si se provee función de envío):
service = EmailNotificationService(send_email)
```

## Posibles extensiones
- Agregar `PushNotificationService` o `SMSNotificationService` como nuevas estrategias.
- Extender la fábrica para leer selección desde base de datos o archivo de configuración.
- Decorator para añadir logging/metricas alrededor del envío sin tocar estrategias.
