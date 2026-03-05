## Visión general del sistema actual (legacy)

Este documento describe el sistema actual (`legacy/adminweb`) tal y como está implementado hoy, a nivel de **funcionalidades** y **módulos**, sin entrar aún en la nueva arquitectura Django + React que se está creando.

El sistema legacy es un **monolito Django** que cubre:

- Una **landing pública** y flujo de captación de pacientes (marca QMM).
- Gestión de **pacientes**, **terapeutas** y **citas de terapia**.
- Un **panel administrativo** (manager) para operación interna.
- Integración con **pagos online** (Stripe/PayPal).
- Envío de **correos transaccionales** (recordatorios, confirmaciones, cancelaciones, etc.).

Todo el frontend se implementa con **templates de Django** y assets estáticos (HTML/CSS/JS) sin SPA dedicada.

---

## Módulos y apps principales

### 1. `manager` – Panel administrativo

**Rol principal**: personal interno / administrador de la plataforma.

**Responsabilidades funcionales:**

- **Autenticación de staff**:
  - Pantalla de login específica para el panel interno.
  - Manejo de sesión de usuarios staff (basado en auth de Django).
  - Control de acceso a secciones internas.

- **Dashboard de operación**:
  - Vista general de estado del sistema: número de pacientes, terapeutas, citas activas, ingresos, etc.
  - Accesos rápidos a secciones clave (pacientes, terapeutas, citas, pagos, contenido de landing).

- **Navegación y layout del panel**:
  - Sidebar con secciones agrupadas (por ejemplo: Pacientes, Terapeutas, Agenda, Pagos, Landing).
  - Templates basados en AdminLTE (tema de administración con componentes pre-hechos).

- **Configuración de la plataforma**:
  - Posible sección de “Ajustes” donde se gestionan parámetros globales (no necesariamente todos implementados).
  - Entrada a submódulos especializados:
    - Gestión de landing (`page`/`qmm`).
    - Gestión de catálogos (si aplica, por ejemplo tipos de servicio).

**A nivel de templates**:

- Utiliza templates en `templates/manager/` (login, dashboard, layouts).
- Usa CSS/JS específicos ubicados en `static/manager/` (AdminLTE, plugins JS).

---

### 2. `patient` – Gestión de pacientes

**Rol principal**: representa a los pacientes (usuarios finales que reciben terapia).

**Responsabilidades funcionales:**

- **Registro y almacenamiento de datos de pacientes**:
  - Modelo `Patient` con datos personales y de contacto (nombre, email, teléfono, etc.).
  - Asociaciones con citas (`meet`) y, eventualmente, pagos (`pay`).

- **Gestión interna de pacientes (panel)**:
  - Listado de pacientes para el personal interno (vistas tipo tabla).
  - Filtros y búsquedas (por nombre, email, estado).
  - Acceso al detalle de un paciente: historial de citas, pagos, terapeuta asignado, etc.

- **Relación con el flujo público**:
  - Cuando un usuario completa el flujo de reserva desde la landing (`qmm`), se crea/actualiza un registro de paciente.
  - La información de perfil del paciente se reutiliza en futuras citas/pagos.

**A nivel de templates**:

- Se apoya en `templates/patient/` para listas y detalles.
- Integración visual con el panel `manager`.

---

### 3. `therapist` – Gestión de terapeutas

**Rol principal**: terapeutas que ofrecen sesiones de terapia a través de la plataforma.

**Responsabilidades funcionales:**

- **Registro y perfil de terapeutas**:
  - Modelo `Therapist` vinculado a usuarios de Django (`User`) o con credenciales propias.
  - Datos básicos: nombre, especialidad, experiencia, foto, bio, etc.

- **Asociación con agenda y citas**:
  - Cada terapeuta se relaciona con múltiples citas (`meet`).
  - Control de disponibilidad y horarios posibles.

- **Acceso a un panel específico (vía `qmm`)**:
  - Inicio de sesión del terapeuta.
  - Gestión de su propia agenda:
    - Marcar disponibilidad.
    - Bloquear / desbloquear días y franjas horarias.
    - Ver próximas citas y estado (confirmada, pendiente, cancelada).

- **Gestión interna desde `manager`**:
  - Listado de terapeutas para el staff.
  - Alta, baja, modificación de terapeutas.
  - Revisión de carga de trabajo, número de pacientes atendidos, etc.

**A nivel de templates**:

- Templates específicos en `templates/therapist/`.
- Vistas de panel de terapeuta (habitualmente integradas en `templates/qmm/`).

---

### 4. `meet` – Agenda y gestión de citas

**Rol principal**: núcleo de la lógica de agenda.

**Responsabilidades funcionales:**

- **Modelo de cita** (`Meet` o similar):
  - Información básica:
    - Paciente.
    - Terapeuta.
    - Fecha y hora de inicio/fin.
    - Tipo de sesión (online/presencial, duración, etc. si aplica).
  - Estado de la cita:
    - Disponible / bloqueada.
    - Reservada.
    - Confirmada.
    - Cancelada.
    - Reprogramada.

- **Generación y gestión de slots de agenda**:
  - Generación de franjas horarias disponibles para cada terapeuta según su disponibilidad.
  - Bloqueo y desbloqueo de días o tramos horarios:
    - Por parte del terapeuta (desde su panel).
    - Por parte del staff (desde `manager`).

- **Relación con el flujo de reserva pública (`qmm`)**:
  - El usuario en la landing ve las fechas/horas disponibles calculadas en base a `meet`.
  - Al completar el flujo de reserva, se marca una franja como ocupada y se asocia al paciente y terapeuta.
  - En caso de reprogramación, se libera una franja y se ocupa otra.

- **Relación con pagos (`pay`)**:
  - Una cita puede requerir un pago asociado.
  - Solo se considera “confirmada” cuando el pago está completado (según la lógica configurada).

**A nivel de templates**:

- Pantallas de listado de citas y detalle (para staff y terapeuta).
- Formularios de creación/edición de citas.

---

### 5. `pay` – Pagos y pasarelas

**Rol principal**: gestión de transacciones económicas entre pacientes y la plataforma (y, según modelo de negocio, terapeutas).

**Responsabilidades funcionales:**

- **Modelo de pago** (`Pay` o similar):
  - Referencia a cita (`Meet`) o servicio.
  - Monto, moneda, fecha.
  - Estado:
    - Pendiente.
    - Completado.
    - Fallido.
    - Reembolsado (si aplica).
  - Identificadores de pasarela (ID de Stripe/PayPal, etc.).

- **Integración con pasarelas de pago**:
  - Integración con **Stripe** y/o **PayPal**:
    - Creación de órdenes de pago desde el backend.
    - Redirecciones a las pasarelas para completar el pago.
    - Recepción de callbacks / retornos para actualizar el estado del pago.

- **Flujo de checkout desde la landing (`qmm`)**:
  - Tras seleccionar terapeuta, día y hora, el usuario pasa a la fase de pago.
  - Se genera una intención de pago y se redirige a la pasarela correspondiente.
  - Una vez completado el pago:
    - Se actualiza el estado del pago a “completado”.
    - Se actualiza el estado de la cita a “confirmada”.

- **Gestión interna de pagos**:
  - Listado de pagos en el panel `manager`.
  - Posibilidad de revisar historial, filtrar por paciente/terapeuta/estado.
  - Soporte a acciones manuales (por ejemplo, marcar un pago como verificado).

**A nivel de templates**:

- Vistas de checkout y confirmación dentro de `templates/qmm/`.
- Listados de pagos en `templates/pay/` o integrados en `manager`.

---

### 6. `qmm` – Landing pública y flujo de negocio principal

**Rol principal**: interfaz de cara al usuario final (público general y, en parte, terapeutas).

**Responsabilidades funcionales:**

- **Landing / marketing**:
  - Página de inicio con copy de venta, secciones de valor, FAQs, testimonios, etc.
  - Presentación de beneficios del servicio de terapia ofrecido.
  - Se apoya en contenido gestionado desde `page` (ver más abajo).

- **Flujo de reserva de terapia (multi-paso)**:
  - Paso 1: selección de tipo de servicio / categoría (si aplica).
  - Paso 2: selección de terapeuta (o asignación automática según reglas).
  - Paso 3: selección de fecha y hora disponibles (consulta a `meet`).
  - Paso 4: datos del paciente (nuevo o existente).
  - Paso 5: resumen + pago (integración con `pay`).
  - Paso 6: confirmación de cita y envío de correo.

- **Gestión de reprogramaciones y cancelaciones**:
  - Enlaces en correos para reprogramar o cancelar cita.
  - Vistas que:
    - Liberan la franja horaria actual.
    - Permiten elegir una nueva franja (en caso de reprogramar).
    - Actualizan el estado de la cita a “cancelada” cuando aplica.

- **Panel de terapeuta (parte pública protegida)**:
  - Login de terapeuta.
  - Vista de agenda de próximas citas.
  - Herramientas para:
    - Marcar disponibilidad.
    - Bloquear / desbloquear días enteros o rangos de tiempo.
    - Visualizar estado de pagos asociados (si se expone).

- **Mensajería y feedback al usuario**:
  - Mensajes de éxito / error después de acciones críticas (reserva, pago, cancelación).
  - Páginas de “gracias”, “error en el pago”, “cita no disponible”, etc.

**A nivel de templates y estáticos**:

- Templates en `templates/qmm/` para:
  - Landing.
  - Formularios del flujo de reserva.
  - Pantallas de pago, confirmación, error.
  - Panel del terapeuta.
- Assets modernos en `static/qmm/`:
  - CSS y JS propios, posiblemente basados en librerías tipo Now UI u otros kits de UI.

---

### 7. `page` – Gestión de contenido de landing

**Rol principal**: permitir que el contenido de la landing y páginas informativas sea editable sin tocar código.

**Responsabilidades funcionales:**

- **Modelos de contenido**:
  - `Page`: página o sección principal (home, preguntas frecuentes, sobre nosotros, etc.).
  - `Section`, `Step`, `Benefit`, `FAQ` u otros modelos que describen bloques de contenido reordenables.

- **Edición desde el panel `manager`**:
  - Listado de páginas/secciones.
  - Formularios para editar:
    - Títulos, subtítulos, textos largos.
    - Ítems de listas (beneficios, pasos del proceso, FAQs).
    - Imágenes o iconos (si aplica).

- **Consumo desde `qmm`**:
  - La landing y otras páginas públicas leen estos modelos para renderizar el contenido.
  - Permite cambiar copys y estructuras sin desplegar una nueva versión de código.

**A nivel de templates**:

- Formularios y listados en `templates/page/` (normalmente integrados visualmente en `manager`).

---

### 8. `siteconfig` – Configuración global del proyecto legacy

**Rol principal**: configuración de Django para el monolito legacy.

**Responsabilidades funcionales:**

- **`settings.py`**:
  - Registro de todas las apps (`manager`, `patient`, `therapist`, `meet`, `pay`, `qmm`, `page`, etc.).
  - Configuración de base de datos (principalmente SQLite en la versión actual).
  - Configuración de:
    - Templates (rutas de `templates/`).
    - Archivos estáticos (`static/`).
    - Sistema de correo para envío de emails transaccionales.
    - Middleware y autenticación.

- **`urls.py`**:
  - Montaje de rutas:
    - `admin/` (Django admin).
    - `manager/` (panel administrativo propio).
    - `qmm/` y/o raíz `/` redirigida a la landing de QMM.
    - Rutas específicas para reprogramación/cancelación, etc.

---

## Funcionalidades transversales

### Autenticación y autorización

- Uso del sistema de usuarios de Django para:
  - Staff interno (acceso a `manager`).
  - Terapeutas (acceso a su panel).
- Control de acceso a vistas mediante decoradores o mixins (login requerido, permisos).
- Gestión básica de sesión y logout.

### Emails transaccionales

- Plantillas en `templates/mails/` para:
  - Confirmación de reserva de cita.
  - Recordatorios previos a la cita.
  - Confirmación de pago (si aplica).
  - Notificaciones de cancelación o reprogramación.
- Envío de correos desde señales o vistas clave (creación de cita, cambio de estado, pago completado).

### Estilos y experiencia de usuario

- **Panel interno (`manager`)**:
  - Basado en **AdminLTE** y plugins asociados:
    - DataTables para tablas interactivas.
    - Select2, datepickers, etc. para formularios.
  - UI pensada para uso interno, no optimizada para una UX moderna y altamente escalable.

- **Landing y flujo público (`qmm`)**:
  - Estética más moderna, con assets propios.
  - No obstante, implementada sobre templates renderizados en servidor, lo que complica la escalabilidad UX frente a un SPA moderno.

---

## Resumen conceptual

En conjunto, el sistema legacy:

- **Cubre ya la mayoría de los bloques funcionales de negocio**:
  - Captación de leads y pacientes desde la landing.
  - Gestión interna de pacientes, terapeutas y citas.
  - Agenda dinámica con disponibilidad y slots.
  - Flujo de reserva y pago online.
  - Panel administrativo para operación diaria.
  - Gestión de contenido de la landing.

- **Presenta limitaciones técnicas y de arquitectura**:
  - Monolito con frontend basado en templates de servidor que dificulta una UX moderna y la evolución rápida del producto.
  - Arquitectura de datos y configuración actual de base de datos (SQLite) no preparada para el escalado esperado.
  - Integraciones (pagos, agenda, contenido) fuertemente acopladas al rendering server-side.

Este documento sirve como **mapa funcional** del sistema actual, que se usará como referencia para el rediseño completo en la nueva arquitectura: backend Django API-first (`backend/`) y frontend React + TypeScript + Tailwind (`frontend/`).

