# Database Models and Schema 🗄️

This document explains the core database schema of RadiographXpress and how the different entities interact. The project uses Django's ORM.

## User Roles (Inheritance from AbstractUser/User)

The system relies on Django's built-in `User` model for authentication, but extends contextual information via One-To-One profile models. Roles are strictly enforced using Django `Group` permissions (`Patients`, `Doctors`, `Associates`, `Assistants`).

### Profiles

1.  **`patientsDashboard.Patient`**
    *   `user`: OneToOneField to `auth.User`.
    *   `mrn`: Medical Record Number (Internal).
    *   `raditech_patient_id`: The ID linking the patient to the external Raditech PACS.
    *   `associated_doctors`: A **ManyToManyField** to `AssociateDoctor`. This relationship is the core of the privacy model.
    *   `profile_picture`: ImageField mapped to AWS S3.

2.  **`doctorsDashboard.ReportingDoctor`** (Radiologists)
    *   `user`: OneToOneField to `auth.User`.
    *   `professional_id`: Medical License Number.
    *   `signature`: ImageField (PNG) used to dynamically sign PDF reports.

3.  **`associateDoctorDashboard.AssociateDoctor`** (Referring Physicians)
    *   `user`: OneToOneField to `auth.User`.
    *   `professional_id`: Medical License Number (Enforced unique constraint for security).
    *   `specialty`: String identifying their branch.
    *   `is_verified`: Boolean. Defaults to `False`. They cannot access the system until an Assistant verifies their license manually.

4.  **`assistantDashboard.Assistant`**
    *   `user`: OneToOneField to `auth.User`.

## Core Domain Models (`core` app)

The `core` app holds the entities related to the radiological workflow.

### 1. `StudyRequest`
*   Created by Assistants when a patient arrives.
*   Contains basic metadata (`request_date`, `notes`) and links to the `Patient`.
*   Acts as the preliminary anchor before the actual study images arrive from Raditech.

### 2. `Study`
*   The fundamental unit of work. Represents a complete radiological exam (e.g., "MRI of the Knee").
*   `id_study_request`: ForeignKey linking back to the initial request.
*   `accession_number` & `raditech_visit_id`: Critical foreign identifiers linking this local record to the DICOM meta-data in Raditech's PACS.
*   `status`: CharField with choices:
    *   `Pending`: Images arrived, waiting for a radiologist.
    *   `In Progress`: A radiologist has "locked" the study and is writing the report.
    *   `Completed`: The report is signed and published.
*   `locked_by`: ForeignKey to `ReportingDoctor`. Enables concurrent workflow by preventing two doctors from diagnosing the same study.

### 3. `Report`
*   The final dictated diagnostic result.
*   `study`: OneToOneField to `Study`. Every study has exactly one report.
*   `doctor`: ForeignKey to `ReportingDoctor` (the author).
*   `findings`, `conclusions`, `recommendations`, `patients_description`: TextFields containing the medical assessment.
*   `date`: Auto-populated on creation. Defines the timestamp of the signature.

## ERD (Entity Relationship Diagram) Simplified

```text
auth.User 1 --- 1 Patient
auth.User 1 --- 1 ReportingDoctor
auth.User 1 --- 1 AssociateDoctor
auth.User 1 --- 1 Assistant

Patient * --- * AssociateDoctor (Granted Access)

Patient 1 --- * StudyRequest
StudyRequest 1 --- 1 Study

Study 1 --- 1 Report
ReportingDoctor 1 --- * Report
ReportingDoctor 1 --- * Study (via locked_by)
```

## Important Developer Notes

*   **Avoid Raw Deletions:** Use `is_active` flags on the `User` model when possible to maintain medical history integrity.
*   **Doctor Properties:** `ReportingDoctor` and `AssociateDoctor` models use `@property` decorators to expose `first_name` and `last_name` from the underlying standard Django `User` object. Do not attempt to save `first_name` directly to the profile models.
