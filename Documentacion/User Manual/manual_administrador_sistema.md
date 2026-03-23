# Manual de Usuario: Administrador del Sistema (Django Admin)

Este manual está dirigido al Administrador de Negocios o Administrador Técnico. El panel de administración proporciona control total sobre los permisos, usuarios, roles y todos los datos en la base de datos subyacente de RadiographXpress.

## 1. Acceso al Panel de Control Administrativo

El panel de control (Django Admin) es un portal oculto y de acceso restringido diseñado exclusivamente para el personal gerencial y de TI.

1. Navega a la URL de administración del sistema (generalmente `http://[tudominio.com]/admin`).
2. Ingresa tus credenciales de superusuario o de staff autorizadas.
3. Al ingresar, serás dirigido al Panel Principal donde se listan todas las entidades ("Aplicaciones") de la base de datos de RadiographXpress.

---

## 2. Gestión de Registros y Roles de Usuario

El núcleo del sistema RadiographXpress se basa en **Grupos** de permisos (`Groups`). Cuando un usuario se registra por la interfaz gráfica, se le asigna a un Grupo.

### Usuarios (`Users`)
1. En la sección **Authentication and Authorization**, haz clic en **Users**.
2. Aquí verás todos los usuarios registrados en el sistema, sea cual sea su rol.
3. **Modificar un usuario:** Si un usuario olvida su contraseña o necesita ser dado de baja, puedes hacer clic en su correo electrónico.
   - **Cambiar contraseña:** Existe un formulario especializado para cambiar claves de acceso directamente.
   - **Activar/Desactivar:** Desmarcando la casilla `Active` puedes suspender temporalmente el acceso de un usuario sin borrar sus datos clínicos asociados.

### Grupos (`Groups`)
El sistema usa 4 grupos principales: `Patients`, `Associates`, `Doctors`, `Assistants`.
- Al entrar a un usuario específico, puedes añadir o quitar grupos en la sección **Permissions**. Esto define qué menú de navegación cargará cuando inicien sesión.

---

## 3. Administración de Perfiles Específicos

En el panel principal verás secciones separadas para cada rol. Aquí gestionarás datos demográficos o perfiles vinculados:

### Médicos Reportadores (`doctorsDashboard`)
Si contratas a un radiólogo nuevo, deberás crearle un usuario y asignarlo a este perfil:
1. Asegúrate de haber creado primero el "Usuario" (Paso 2).
2. Entra a `Reporting doctors` y haz clic en **Add**.
3. Selecciona el Usuario correspondiente.
4. **Firma Digital (`Signature`):** Como administrador, puedes subir tú mismo el archivo PNG de la firma autógrafa del doctor si él no puede hacerlo, para que empiece a reportar inmediatamente.
5. Puedes validar el prefijo de especialidad (p. ej., "Dr. Juan Pérez" vs "Dr. Miguel López").

### Asistentes (`assistantDashboard`)
1. Administra los perfiles del staff del front-desk.
2. Similar al médico reportador, puedes vincular perfiles de `Users` a perfiles de `Assistants`.
3. Es recomendable revisar qué cajera/asistente está usando qué perfil para auditorías futuras de quién admitió a quién.

---

## 4. Auditoría Clínica: Pacientes y Estudios

A través del panel, tienes un historial directo a los datos crudos del sistema.

### Pacientes (`patientsDashboard`)
1. En **Patients**, verás a todos los pacientes.
2. Aquí puedes visualizar y modificar:
   - Su "Medical Record Number" (`MRN`) interno de la clínica.
   - El ID de Raditech que sincroniza las facturas e historiales numéricos con el PACS viejo.
   - Los médicos de cabecera a quienes ellos han autorizado dar vista (`Associated Doctors`). Puedes revocar accesos en nombre del paciente si es requerido por ley o por una petición formal.

### Referentes / Médicos Asociados (`associateDoctorDashboard`)
1. Ve a **Associate doctors**.
2. Como administrador general, puedes activar (`is_verified`) a médicos que no hayan sido procesados por el mostrador/front-desk aún.
3. Aquí podrás ver la cédula profesional (`professional_id`) ligada a cada perfil para realizar las verificaciones legales correspondientes.

### Estudios y Reportes Core (`core`)
En casos de soporte técnico o peticiones de las autoridades pertinentes para re-expedir un documento original:
1. En la sección **Studies**, puedes buscar un paciente, ver con qué "Study Request" entró el registro y qué fecha tiene.
2. En la sección **Reports**, puedes observar los textos dictaminados de cada interpretación realizada, incluyendo el timestamp y el doctor que lo firmó.

---

## 5. Mantenimiento y Buenas Prácticas

- **Nunca elimines (Delete) un registro** (Usuario, Estudio o Reporte) a menos que haya sido un error tipográfico en un ambiente de prueba. Utiliza la bandera `Active=False` para preservar la integridad de datos transaccionales, históricos y obligaciones médico-legales.
- **Auditoría regular:** Se aconseja revisar los perfiles en el estado `Staff Status=True` mensualmente, para asegurarse de que ex-empleados no retengan acceso confidencial al panel administrativo de Django.
