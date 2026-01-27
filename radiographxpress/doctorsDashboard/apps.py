from django.apps import AppConfig


class DoctorsdashboardConfig(AppConfig):
    name = 'doctorsDashboard'

    def ready(self):
        import doctorsDashboard.signals
