# Capturas de Pantalla Pendientes: Correos Electrónicos (SMTP)

Debido a que el despliegue del sistema de correos es externo o automatizado y depende del gestor de correo configurado (GMAIL, AWS SES, etc.), **debes realizar capturas manualmente de tu propia bandeja de entrada** cuando pruebes el sistema para añadirlas a tus manuales (si deseas graficar esos flujos en tu PDF o al compilar LaTeX).

A continuación se enlistan las capturas recomendadas y en qué sección de tus manuales deben colocarse (usando el comando `\includegraphics{}` de LaTeX):

## 1. Validación de Cuenta Nueva (Pacientes)
**Tipo de Captura:** Una fotografía/screenshot del correo que recibe el paciente llamado "Activa tu cuenta de RadiographXpress".
- **Recomendación Visual:** Muestra el logo del hospital en el correo y el botón/link de "Verificar Correo".
- **¿A qué manual pertenece?** `manual_paciente.tex` 
- **¿Dónde colocarla en LaTeX?** Debajo de la sección `1.1 Crear una Cuenta Nueva`, en los pasos de **Verificación**. Nómbrala `email_validacion_paciente.png` y añádela como:
  ```latex
  \begin{figure}[h]
      \centering
      \includegraphics[width=0.7\textwidth]{email_validacion_paciente.png}
      \caption{Correo de verificación de cuenta del paciente.}
  \end{figure}
  ```

## 2. Validación de Médico Asociado (Pendiente Administrativo)
**Tipo de Captura:** Un screenshot del correo de recibo inicial de documentación para doctores.
- **¿A qué manual pertenece?** `manual_medico_asociado.tex`
- **¿Dónde colocarla en LaTeX?** Sección `1.2 Validaciones y Aprobación`. Nómbrala `email_esperando_aprobacion.png`.

## 3. Notificación de Médico Aprobado
**Tipo de Captura:** Un screenshot del correo notificando al Doctor Asociado que el Auxiliar o Asistente aprobó su cédula profesional e identidad.
- **¿A qué manual pertenece?** `manual_medico_asociado.tex`
- **¿Dónde colocarla en LaTeX?** Al finalizar la sección `1.2 Validaciones y Aprobación`. Nómbrala `email_medico_aprobado.png`.

## 4. Resetear Contraseña (Opcional)
**Tipo de Captura:** Correo en el caso que el usuario olvidó su contraseña ("Recuperación de clave").
- **¿A qué manual pertenece?** A todos los manuales si decides documentarlo. Nómbrala `email_password_reset.png`.

---

**Nota Técnica para Overleaf / Editor LaTeX:** 
Una vez tomes estas capturas con la herramienta de recortes de tu computadora, colócalas dentro de la carpeta `screenshots/` de tu proyecto y asegúrate de que el nombre del archivo coincida exactamente con las directivas en el código de arriba.
