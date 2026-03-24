# Diagrama de Entidad-Relación (ERD)

A continuación se presenta el diagrama detallado de la base de datos de RadiographXpress. El sistema utiliza el ORM de Django, apoyándose fuertemente en relaciones "One-to-One" con el modelo estándar de Autenticación (`auth.User`) para manejar los perfiles y roles.

```mermaid
erDiagram
    %% Core Django Model
    USER {
        int id PK
        string username
        string email
        string password
        string first_name
        string last_name
        boolean is_active
    }

    %% User Profiles (Dashboards)
    PATIENT {
        int id PK
        int user_id FK "O2O a User"
        string mrn "Medical Record Number"
        string raditech_patient_id "ID externo"
        boolean is_email_verified
        string profile_picture
    }

    ASSOCIATE_DOCTOR {
        int id PK
        int user_id FK "O2O a User"
        string professional_id "Cédula (Unique)"
        string specialty
        boolean is_verified
        string profile_picture
    }

    REPORTING_DOCTOR {
        int id PK
        int user_id FK "O2O a User"
        string professional_id "Cédula"
        string signature "Firma (PNG/JPG)"
        string profile_picture
    }

    ASSISTANT {
        int id PK
        int user_id FK "O2O a User"
        string profile_picture
    }

    %% Core Application Models
    STUDY_REQUEST {
        int id PK
        int patient_id FK "Relación a Patient"
        date request_date
        text notes
    }

    STUDY {
        int id PK
        int id_study_request FK "Relación a StudyRequest"
        string accession_number "Identifier PACS"
        string raditech_visit_id "Identifier API"
        string study_name
        string modality
        date date
        string status "Pending, In Progress, Completed"
        int locked_by FK "Relación a ReportingDoctor (Opcional)"
    }

    REPORT {
        int id PK
        int study_id FK "O2O a Study"
        int doctor_id FK "Relación a ReportingDoctor"
        text patients_description
        text findings
        text conclusions
        text recommendations
        datetime date "Timestamp de Firma"
    }

    %% Relationships
    USER ||--o| PATIENT : "OneToOne"
    USER ||--o| ASSOCIATE_DOCTOR : "OneToOne"
    USER ||--o| REPORTING_DOCTOR : "OneToOne"
    USER ||--o| ASSISTANT : "OneToOne"

    PATIENT }|--|{ ASSOCIATE_DOCTOR : "ManyToMany (associated_doctors)"

    PATIENT ||--o{ STUDY_REQUEST : "OneToMany"
    STUDY_REQUEST ||--o| STUDY : "OneToOne/ForeignKey"

    STUDY ||--o| REPORT : "OneToOne"
    
    REPORTING_DOCTOR ||--o{ STUDY : "OneToMany (locked_by)"
    REPORTING_DOCTOR ||--o{ REPORT : "OneToMany"
```

## Detalles de las Relaciones Críticas

*   **Confidencialidad:** La relación *Many-To-Many* (`associated_doctors`) entre `Patient` y `AssociateDoctor` es la que determina qué médicos externos pueden visualizar los expedientes clínicos de qué pacientes. Si no existe un registro en esta tabla pivote, el acceso es denegado (`HTTP 403`).
*   **Bloqueos Conexos (Locks):** La llave foránea `locked_by` en la tabla `Study` apunta al radiólogo (`ReportingDoctor`) que está dictaminando el estudio actualmente. Cuando este valor no es nulo y el estado es `In Progress`, la UI inhabilita el estudio para el resto del hospital.
*   **Sincronización Múltiple:** El `StudyRequest` nace manualmente por el Asistente, mientras que el `Study` se genera asíncronamente vía el PACS (Sincronizador Raditech). Ambos se correlacionan a través de la llave foránea `id_study_request`.
