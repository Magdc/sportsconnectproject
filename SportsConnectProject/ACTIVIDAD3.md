# Inversión de Dependencias e Inyección en SportsConnect

## Caso aplicado: Sistema de notificaciones
En este proyecto, el envío de notificaciones (por ejemplo, confirmaciones de reserva) estaba acoplado a una función concreta de envío de correo electrónico. Esto dificultaba cambiar el mecanismo de notificación (por ejemplo, para pruebas, logs, o nuevos canales como SMS).

### Solución implementada
1. **Se creó una abstracción NotificationService** (ver `notification_services.py`), que define el método `send`.
2. **Se implementaron dos servicios concretos:**
   - `ConsoleNotificationService`: Muestra la notificación en consola.
   - `EmailNotificationService`: Usa la función de envío de correo real.
3. **Las funciones de confirmación** (`reserva_confirmacion` y `WaitList_confirmacion`) ahora reciben el servicio de notificación como parámetro (inyección de dependencia). Si no se especifica, usan la consola por defecto.

### Ejemplo de uso
```python
# Por defecto (consola):
reserva_confirmacion(request, email, nombre, fecha, hora)

# Inyectando el servicio de email:
from reservation.notification_services import EmailNotificationService
notifier = EmailNotificationService(send_email)
reserva_confirmacion(request, email, nombre, fecha, hora, notification_service=notifier)
```

## Beneficios
- **Desacoplamiento:** El código de alto nivel no depende de detalles concretos.
- **Testabilidad:** Se pueden inyectar mocks o servicios de prueba fácilmente.
- **Extensibilidad:** Es sencillo agregar nuevos canales de notificación.

---

Este patrón mejora la mantenibilidad y flexibilidad del sistema, alineándose con buenas prácticas de arquitectura de software.