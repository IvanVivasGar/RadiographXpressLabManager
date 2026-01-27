# radiograph-xpress

### Descripción del proyecto

En colaboración con Radiograph-Xpress, este proyecto se centra en la digitalización completa y la modernización de los procesos administrativos y médicos. Nuestro objetivo es situar a la compañía a la vanguardia del mercado, garantizando agilidad, comodidad y funcionalidad en todas sus operaciones.

Al eliminar la necesidad de procesos manuales y tardados, este sistema se establece como una herramienta de suma relevancia en un área donde la rapidez es crítica. No solo apoyaremos la agilidad operativa interna de Radiograph-Xpress, sino que también mejoraremos al máximo la experiencia del cliente, a menudo tensa, proporcionando resultados rápidos y accesibles.

## Objetivos y Alcance
### Objetivos

La esencia del proyecto radica en transformar los flujos de trabajo lentos y manuales en un sistema digital eficiente. Esto incluye:

1. Creación de una Base de Datos Robusta: Digitalización de todos los estudios y análisis para generar un repositorio de información de alta relevancia y fácil acceso.

2. Optimización del Servicio al Cliente: Mejorar significativamente la experiencia del paciente al habilitar la distribución de resultados de estudios y análisis a través de plataformas digitales (correo electrónico, portal web, etc.).

3. Facilitación de la Colaboración Médica: Implementar una funcionalidad para que los médicos remitentes puedan recibir y consultar directamente los estudios de sus pacientes a través de la plataforma, agilizando el diagnóstico y tratamiento.

4. Digitalización del Análisis y Diagnóstico: Integrar el proceso de análisis de estudios directamente en la plataforma digital, eliminando la dependencia de documentos físicos.

### Alcance

El proyecto cubre los siguientes requerimientos: <br>
### Requerimientos Funcionales: <br>
1. RF001: El sistema debe permitir el registro de un paciente para generar una cuenta. (Nombre completo, contraseña, email, dirección y telefono).
2. RF002a: El sistema debe permitir a un usuario administrador, crear, leer, actualizar y eliminar usuarios de doctores que realizaran los análisis de las radiografías.
3. RF002b: El sistema debe permitir usuarios 'Doctor' que realizaran los análisis de los estudios, estos deberán ser creados por el usuario administrador unicamente.
4. RF003: El sistema debe almacenar reportes de los estudios y las solicitudes de estos estudios en una base de datos.
5. RF004a: El sistema debe permitir, en caso de que un estudio sea solicitado por un doctor para un paciente suyo, una cuenta para este doctor, como un 'asociado'.
6. RF004b: El sistema debe almacenar y asociado las solicitudes y estudios pedidos por un doctor 'asociado' en la base de datos, para generar un historial de este mismo.
7. RF005: El sistema debe enviar los estudios y analisis al paciente a traves de una plataforma digital, asi como, de ser el caso, a su doctor 'asociado'.
8. RF006: El sistema debe mandar los resultados de los estudios, así como su radiografía bajo una contraseña generada automaticamente.
9. RF007: El sistema debe asociar los estudios a sus doctores, de manera que se lleve un historial de los estudios realizados por cada doctor.
10. RF08: El sistema debe generar una cola con las radiografías realizadas que estan esperando analisis, de manera que se puedan agilizar los procesos.
11. RF009: El sistema debe generar el reporte con la estructura proporcionada por Radiograph-Xpress, este reporte debe estar membretado y firmado (digitalmente).
12. RF010: El sistema debe automatizar el proceso de subida de la radiografía a la nube.
13. RF011: El sistema deberá pedir una cedula profesional a sus doctores, tanto asociados como de analisis.
14. RF012: El sistema deberá certificar la autenticidad de la cedula profesional de los doctores, especialmente de aquellos que realizarán los estudios, de otra manera no estaran autorizados para hacer los estudios.
15. RF013: El sistema tendra un bot guía que ayudara a los pacientes con poco o nulo conocimiento en la web a navegar en la interfaz y localizar sus estudios.
16. RF014: El sistema deberá asignar los estudios automaticamente, acorde al asunto del estudio llenado en la solicitud de estudio y la especialidad del doctor.

### Requerimientos No Funcionales:<br>
1. RNF001: El sistema debe encriptar la base de datos para proteger datos sensibles del paciente, doctor 'aspociado', asi como de la empresa.
2. RNF002: El estudio (radiografía y análisis) deben de estar protegidos bajo contraseña.
3. RNF003: El sistema debe de tener como máximo, 2 horas al mes de inutilidad para el mantenimiento.
4. RNF004: El sistema debe recibir mantenimiento el día (por determinar), a las (hora por determinar).
5. RNF005: En caso de falla, el sistema no puede estar inoperante por más de 1 hora.
6. RNF006: El sistema debe permitir, unicamente a un administrador, ver los analisis y reportes de todos los doctores.
7. RNF007: El sistema debe permitir a cada doctor, ver unicamente los estudios que aquel doctor haya realizado.
8. RNF008: El sistema debe permitir al paciente ver sus estudios en la plataforma, unicamente los suyos.
9. RNF009: El sistema debe estar protegido ante el OWASP TOP 10.
10. RNF010: El sistema no debe permitir SQL Injections.
11. RNF011: El sistema debe tener logs para la manipulación de la arquitectura del proyecto.
12. RNF012: El sistema por parte del paciente debe ser utilizable para una persona de una escolaridad primaria o superior.
13. RNF013: Se hará una capacitación de una semana para los usuarios doctores.
14. RNF014: Las consultas de estudios y analisis se deberan hacer exitosamente bajo 1 segundo.
15. RNF015: El despliegue de la aplicación se hará sobre AWS (Amazon Web Services). <- PUNTO A DETERMINAR CON RADIOGRAPH
16. RNF016: REQUERIMIENTO PARA LA HERRAMIENTA DE DIGITALIZACION DE RADIOGRAPHXPRESS. <- PUNTO POR COMPLETAR
17. RNF017: El diseño de la aplicación seguirá la paleta de colores de Radiograph-Xpress, como de, tentativamente, su pagina web.
18. RNF018: Se deberá realizar un manual de usuario para RadiographXpress, para el uso de la aplicación por parte de los doctores, asi como de sus administradores.
19. RNF019: El sistema deberá cumplir con la Ley General de Protección de Datos Personales en Posesión de Sujetos Obligados.
20. RNF020: El sistema deberá cumplir con la Ley Federal de Protección de Datos Personales en Posesión de los Particulares.
21. RNF021: El sistema deberá cumplir con las regulaciones siguientes(para en caso de tener pacientes de la UE o de los EUA): GDPR, HIPAA (Ley de Portabilidad y Responsabilidad de Seguros de Salud en Estados Unidos).
22. RNF022: El sistema debe admitir el uso de autenticación de multiple factor, con herramientas como Google Authenticator o Authy.

## Guía de uso e instalación
### Requisitos previos

### Instalación

### Ejecución

## Estructura del proyecto

## Tecnologías utilizadas
Front-end: React.js<br>
Back-end: Django<br>
Base de datos: (Por Determinar)<br>

## Interfaces

Figma: https://www.figma.com/design/0c7bCiPXTCz5loS00IP4qp/Radiograph-Xpress?node-id=0-1&t=GVjoagr6QOVNSDf7-1
AWS Demo:http://radiograph-xpress-interfaces.s3-website-us-east-1.amazonaws.com

## Autores y Contacto

Iván Vivas García - ivanvivasgar@gmail.com - Universidad La Salle Bajío <br>
Emmanuel Ovalle Magallanes - eom106933@lasallebajio.edu.mx - Universidad La Salle Bajío <br>