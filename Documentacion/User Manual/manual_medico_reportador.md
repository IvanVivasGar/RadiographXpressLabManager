# Manual de Usuario: Médico de Interpretación (Radiólogo)

¡Bienvenido! Este es tu portal principal de operaciones de diagnóstico en RadiographXpress. Como Médico Reportador, aquí dictaminarás, clasificarás y enviarás los resultados a nuestros pacientes y médicos tratantes a través de un sistema de PACS automatizado.

## 1. Ingreso y Configuración Profesional

Tu cuenta es administrada de forma interna; deberás iniciar sesión con las credenciales entregadas por gerencia o TI.

### Tu Perfil y Firma Digital
Es mandatario revisar tu perfil para poder entregar resultados válidos:
1. Ve a las opciones de perfil.
2. **Foto de perfil:** Puedes actualizar tu fotografía.
3. **Firma Electrónica / Firma Digital:** Como obligación, puedes y debes cargar el archivo (usualmente PNG transparente) que contiene tu firma digital o autógrafa escaneada, ya que esta se inyectará automáticamente en los documentos **PDF** de todos los estudios que dictamines. Solo se admiten archivos en formato de imagen aprobado.

---

## 2. Exploración del Tablero (Worklist)

Tu dashboard principal sirve como tu Worklist y bandeja de entrada de estudios. Se sincroniza directamente en tiempo real. 

### Estudios Pendientes (Pending)
Se listan los nuevos estudios referenciados desde Raditech o el sistema PACS/RIS. 
- Estos estudios están esperando interpretación.

### Estudios Terminados (Completed)
Tu historial de todos los reportes que tú has dictaminado y liberado.

---

## 3. Bloqueo e Interpretación de un Estudio

Debido a que pueden existir múltiples radiólogos trabajando al mismo tiempo, el sistema utiliza "Locks" o bloqueos.

### Tomar un estudio ("Locking")
1. Ubica un estudio con estado **"Pending"** en tu worklist.
2. Selecciona **"Interpretar"** o abre el estudio.
3. El sistema cambiará el estatus a **"En Progreso"**.
4. 🔒 **Bloqueo Inteligente:** A partir de ese segundo, ningún otro radiólogo del hospital podrá tomar ese estudio. Automáticamente queda reservado bajo tu cuenta (incluso si cierras tu sesión) hasta que lo termines o lo liberes.

### Redactar y Enviar el Reporte
Dentro de la consola de diagnóstico, debes rellenar los metadatos clínicos:
1. **Descripción de paciente (Motivo de envío)**.
2. **Hallazgos.**
3. **Conclusiones diagnósticas.**
4. **Recomendaciones.**

Una vez completa la nota, presiona en finalizar/enviar.
- El sistema firmará automáticamente.
- El estado cambiará de "En progreso" a **"Completado"**.
- El PDF estará instantáneamente disponible para el paciente en su aplicación, así como para sus médicos asociados.

---

## 4. Consulta de Reportes Anteriores

Como encargado médico, posees niveles de privilegio altos.
Si necesitas consultar la configuración, revisar dictámenes pasados, o extraer un PDF antiguo para un paciente:
1. Ve a la pestaña de Estudios Completados.
2. Haz clic en un estudio guardado.
3. El sistema te desplegará todo el historial tal y como si fueras el paciente.

---

## Notas de Desempeño
- Nunca dejes estudios en progreso indefinidamente. Si detectas que equivocaste la toma de un estudio, contacta al soporte para poder liberar el candado.
- *Tip técnico:* El Websocket y el proceso secundario están vinculando el PACS de manera asíncrona constantemente. Si el estudio aparece pero las imágenes fallan, puede deberse un delay natural del integrador de red Raditech.
