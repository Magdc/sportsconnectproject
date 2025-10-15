# Revisión Autocrítica 

Revisión de calidad, revisando conceptos vistos en clase como Usabilidad, Compatibilidad, Rendimiento y Seguridad.

## Usabilidad
- **Interfaz de usuario:** El sistema utiliza plantillas HTML sencillas y formularios claros para la interacción de los usuarios. Sin embargo, la experiencia podría mejorarse con validaciones en tiempo real y mensajes de error más descriptivos.
- **Accesibilidad:** Actualmente, el sistema no implementa características específicas de accesibilidad (por ejemplo, soporte para lectores de pantalla o navegación por teclado). 
- **Flujo de usuario:** El proceso de reserva y gestión es intuitivo, y cuenta con retroalimentación instantánea de cada acción lo que permite un flujo de usuario más guiado.

## Compatibilidad
- **Navegadores:** El sistema está basado en Django y HTML estándar, por lo que es compatible con los principales navegadores modernos. No se han realizado pruebas con navegadores antiguos ni con otros menos usados.
- **Dispositivos:** El diseño no es completamente responsivo. Se deberian adaptar las plantillas para una mejor visualización en dispositivos móviles y tablets.
- **Dependencias:** El uso de Google OAuth y otras librerías externas requiere una configuración adecuada del entorno.

## Rendimiento
- **Escalabilidad:** El sistema está diseñado para un entorno académico o de pequeña escala. Para soportar mayor concurrencia, sería necesario optimizar consultas a la base de datos y considerar el uso de cachés.
- **Carga:** Las operaciones principales (reservas, consultas) son rápidas bajo carga baja. No se han realizado pruebas de  alto estrés.
- **Optimización:** La aplicación no se encuentra optimizada ni tiene pruebas de rendimiento de algoritmos.

## Seguridad
- **Autenticación y autorización:** Se utiliza el sistema de autenticación de Django y decoradores para proteger vistas sensibles. Sin embargo, que no todas las rutas críticas estén protegidas.
- **Gestión de credenciales:** Las credenciales sensibles (OAuth, tokens) se almacenan en variables de entorno y no en el código fuente, lo que sigue buenas prácticas.
- **Validación de datos:** Existen validaciones básicas, se debe fortalecer la validación de entradas del usuario para prevenir ataques como inyección SQL o XSS.
- **Protección CSRF:** Se utilizan los mecanismos de protección CSRF de Django en la mayoría de los formularios.
- **Nota** Se debe revisar que en las consultas de las reservas se pasa el id como parametro en la URL lo que podría llevar a que usuarios revisaran otras reservas que no deberian.
