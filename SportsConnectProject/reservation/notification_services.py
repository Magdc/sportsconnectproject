from abc import ABC, abstractmethod

class NotificationService(ABC):
    @abstractmethod
    def send(self, user_email, subject, message):
        pass

class ConsoleNotificationService(NotificationService):
    def send(self, user_email, subject, message):
        print(f"[NOTIFICACIÓN] Para: {user_email}\nAsunto: {subject}\nMensaje: {message}")
        return "Notificación mostrada en consola."

# Ejemplo de implementación para email (puede usar la lógica de send_email existente)
class EmailNotificationService(NotificationService):
    def __init__(self, email_sender_func):
        self.email_sender_func = email_sender_func

    def send(self, user_email, subject, message):
        return self.email_sender_func(user_email, subject, message)
