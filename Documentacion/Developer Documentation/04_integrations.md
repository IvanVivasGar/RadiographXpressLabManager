# Third-Party Integrations

RadiographXpress relies on external systems for storing medical media and fetching DICOM/PACS data.

---

## 1. AWS S3 (Media Storage)

To handle user uploads (profile pictures, signatures, future DICOM snapshots) without filling up local container storage, the app relies on **Amazon S3** via `django-storages`.

### Configuration (`settings.py`)

Controlled via environment variables:
*   `USE_S3 = True`
*   `AWS_ACCESS_KEY_ID`
*   `AWS_SECRET_ACCESS_KEY`
*   `AWS_STORAGE_BUCKET_NAME`

If `USE_S3` is True, Django overrides default storage engines:
```python
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

### Developer Impact
Whenever you interact with an `ImageField` models (e.g. `patient.profile_picture.url`), Django transparency generates a signed S3 URL. Do not write local file saving logic for models.

---

## 2. Raditech PACS/RIS API

RadiographXpress does not implement a DICOM server natively. It acts as an abstraction and reporting layer above the **Raditech PACS/RIS API**.

### Raditech API Client (`core/raditech_client.py`)

A singleton HTTP client (`RaditechAPIClient`) manages interaction with the external system.
*   **Authentication:** The API requires dynamic token fetching. On instantiation, the client calls the Raditech Auth endpoint using credentials stored in `.env`.
*   **Token Refresh:** If the token (`access_token`) expires, the client logic automatically catches `401 Unauthorized` responses and re-authenticates.

### Background Synchronization (`sync_pacs_images.py`)

The heart of the integration is a custom Django management command that runs continuously in the background (as the `sync_pacs` Docker container in production).

**Workflow of `sync_pacs_images`:**
1.  **Sleep Loop:** Runs an infinite `while True` loop, pausing for `RADITECH_SYNC_INTERVAL` (default 300s/5mins).
2.  **Fetch Unlinked:** Queries the local DB for `StudyRequest` objects that do not yet have an associated `Study`.
3.  **Fetch Raditech API:** Calls Raditech's `integrations/getStudies` endpoint.
4.  **Matching Logic:** Compares the local `StudyRequest` against incoming `Visits`/`Studies` from PACS using `patient_id` or `accession_number`.
5.  **Creation:** If a match is found and the images are marked as ready in PACS, it creates the local `core.Study` object with status `Pending`.
6.  **Real-Time Trigger:** It then fires a Channel Layer Websocket broadcast so that the new study immediately pops up on the locked Radiologist's screen without them having to refresh.

### Troubleshooting Raditech
If studies stop syncing:
1.  Check the logs of the `sync_pacs` container: `docker-compose logs --tail 200 sync_pacs`.
2.  Verify the authentication keys (`RADITECH_KEY`, `RADITECH_ORG_ID`) have not expired.
3.  Confirm network access out of the container to `https://risapi.grupoptm.com/api`.
