# Patrones de Diseño en Django aplicados

Este documento resume patrones implementados en el proyecto para mejorar mantenibilidad y extensibilidad.

## 1) Signals (Observer) para eventos de dominio
- Archivo: `reservation/signals.py`
- Patrón: Observer a través de señales `post_delete` de Django.
- Caso de uso: Cuando se elimina una `Reservation`, se notifica a los usuarios en `WaitList` para la misma instalación y fecha, usando el servicio de notificaciones (Strategy) seleccionado por la fábrica.
- Beneficios: Desacopla efectos colaterales (notificación) de la lógica principal de borrado, facilitando evolución y pruebas.

## 2) Managers personalizados (Repository-like)
- Archivo: `reservation/models.py` (`WaitListManager`)
- Patrón: Encapsula consultas comunes en un Manager, actuando similar a un repositorio.
- Caso de uso: `WaitList.objects.for_facility_on_date(facility, date)` ordena por antigüedad.
- Beneficios: Reutilización, legibilidad y pruebas más simples, evitando duplicación de filtros.

## 3) Strategy + Factory integrados con Django
- Archivos: `reservation/notification_services.py`, `reservation/notification_factory.py`, `reservation/views.py`
- Patrón: Strategy para canales de notificación; Factory para elegir implementación según entorno (`USE_EMAIL_NOTIFICATIONS`).
- Caso de uso: Confirmaciones de reserva y lista de espera, además de notificaciones por señales.

## Cómo se activa
- `reservation/apps.py` registra `reservation.signals` en `ready()` para que el Observer funcione cuando la app se carga.
- Variable de entorno: `USE_EMAIL_NOTIFICATIONS=true` para activar envío de correos reales (si credenciales Google están configuradas). Caso contrario se usa consola.

## Próximas mejoras sugeridas
- Migrar vistas funcionales críticas a Class-Based Views (CBV) para mayor reutilización.
- Añadir Decorators/Permissions específicos en CBVs y mezclar con `LoginRequiredMixin`.
- Implementar un patrón Service Layer para operaciones de reserva complejas.
