import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radiographxpress.settings')
django.setup()

from doctorsDashboard.models import Patient, Study, AssociatedDoctor, StudyRequest, Study

def populate():
    print("Populating mock data...")

    # Create Associated Doctor
    assoc_doc, created = AssociatedDoctor.objects.get_or_create(
        id_associated_doctor='DOC123',
        defaults={
            'name': 'Gregory',
            'last_name': 'House',
            'password': 'password123',
            'email': 'house@hospital.com',
            'address': 'Princeton-Plainsboro',
            'phone': '555-0199'
        }
    )
    
    # Create Patient
    patient, created = Patient.objects.get_or_create(
        name='Miriam',
        last_name='Hernandez Gonzalez',
        defaults={
            'password': 'password123',
            'email': 'miriam@example.com',
            'address': '123 Main St',
            'phone': '555-5555'
        }
    )
    
    # Create Study Request
    request, created = StudyRequest.objects.get_or_create(
        id_solicitud_estudio=1001,
        defaults={
            'email_doctor': 'house@hospital.com',
            'diagnosis': 'Possible Fracture',
            'requested_study': 'X-Ray Thorax',
            'id_associated_doctor': assoc_doc
        }
    )

    # Create Pending Studies (Mocking the data from the React component)
    # Using a placeholder URL that could be an iframe content
    mock_studies = [
        {'id': 1, 'date': date(2023, 10, 25)},
        {'id': 2, 'date': date(2023, 10, 26)},
        {'id': 3, 'date': date(2023, 10, 27)},
        {'id': 4, 'date': date(2023, 10, 28)},
    ]

    for s_data in mock_studies:
        Study.objects.get_or_create(
            id_study_request=request,
            id_patient=patient,
            date=s_data['date'],
            defaults={
                'pacs_url': 'https://images.grupoptm.com/?sp=dcb37163-de37-4856-83f0-7abb4db2a229&org=GPTM&wf=68e558107712dd7d0a0fbbb6&suid=1.2.840.113619.2.227.207924731240.21703251007104128.20000&aet=GPTMRADIOG&et=20&ep=eb4b0906-034b-4ddd-b5bb-4a51fbeaf810', # Public valid DICOM viewer for demo
                'status': Study.PENDING,
                'email_sent': False,
                'password': 'studypassword'
            }
        )
        
    print(f"Created {Study.objects.count()} studies.")

if __name__ == '__main__':
    populate()
