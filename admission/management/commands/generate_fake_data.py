import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from admission.models import (  # Update this import based on your app name
    Department, Room, RoomFacility, Bed, BedMaintenance, Patient,
    PatientMedicalProfile, PatientEmergencyContact, Admission,
    AdmissionDiagnosis, AdmissionVitals, TreatmentPackage, PackageService,
    AdmissionService, Billing, Payment, InsuranceClaim, MedicalStaff, StaffProfile
)

fake = Faker()


class Command(BaseCommand):
    help = "Generate fake data for hospital models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--models",
            nargs="+",
            type=str,
            help="Specify models to populate (default: all models).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        models_to_populate = options["models"]

        self.stdout.write(self.style.SUCCESS(
            "Starting fake data generation..."))

        try:
            if not models_to_populate or "medical_staff" in models_to_populate:
                self.generate_medical_staff()

            if not models_to_populate or "Department" in models_to_populate:
                self.generate_departments()

            if not models_to_populate or "Room" in models_to_populate:
                self.generate_rooms()

            if not models_to_populate or "RoomFacility" in models_to_populate:
                self.generate_room_facilities()

            if not models_to_populate or "Bed" in models_to_populate:
                self.generate_beds()

            if not models_to_populate or "Patient" in models_to_populate:
                self.generate_patients()

            if not models_to_populate or "Admission" in models_to_populate:
                self.generate_admissions()

            self.stdout.write(self.style.SUCCESS(
                "✅ Fake data generation completed successfully."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            raise e  # Ensures rollback of changes

    def generate_departments(self, count=5):
        """Generate fake departments"""
        for _ in range(count):
            Department.objects.create(
                name=fake.unique.company(),
                description=fake.text()
            )

    def generate_rooms(self, count=10):
        """Generate fake rooms"""
        departments = list(Department.objects.all())
        room_types = [choice[0] for choice in Room.ROOM_TYPES]

        for _ in range(count):
            Room.objects.create(
                department=random.choice(departments),
                room_number=fake.unique.random_int(100, 999),
                room_type=random.choice(room_types),
                floor=random.randint(1, 5),
                is_operational=fake.boolean(),
                capacity=random.randint(1, 4),
            )

    def generate_room_facilities(self):
        """Generate facilities for each room (ensuring one per room)"""
        for room in Room.objects.all():
            RoomFacility.objects.update_or_create(
                room=room,
                defaults={
                    "has_ventilator": fake.boolean(),
                    "has_oxygen": fake.boolean(),
                    "has_suction": fake.boolean(),
                    "has_cardiac_monitor": fake.boolean(),
                    "has_defibrillator": fake.boolean(),
                }
            )

    def generate_beds(self, count=20):
        """Generate fake beds"""
        rooms = list(Room.objects.all())
        bed_types = [choice[0] for choice in Bed.BED_TYPES]

        for _ in range(count):
            room = random.choice(rooms)
            bed_number = fake.unique.random_int(1, 50)

            Bed.objects.create(
                room=room,
                bed_number=str(bed_number),
                bed_type=random.choice(bed_types),
                is_available=fake.boolean(),
                is_operational=fake.boolean(),
            )

    def generate_patients(self, count=10):
        """Generate fake patients"""
        genders = [choice[0] for choice in Patient.GENDER_CHOICES]

        for _ in range(count):
            # age = fake.age()
            Patient.objects.create(
                name=fake.name(),
                age=random.randint(1, 50),
                gender=random.choice(genders),
                contact_number=fake.phone_number(),
                email=fake.email(),
                address=fake.address(),
            )

    def generate_admissions(self, count=5):
        """Generate fake admissions"""
        patients = list(Patient.objects.all())
        beds = list(Bed.objects.filter(is_available=True))

        if not patients or not beds:
            return

        status_choices = [choice[0] for choice in Admission.STATUS_CHOICES]

        for _ in range(count):
            patient = random.choice(patients)
            bed = random.choice(beds)
            admission_date = fake.date_time_between(
                start_date="-30d", end_date="now")

            Admission.objects.create(
                patient=patient,
                bed=bed,
                admission_date=admission_date,
                discharge_date=admission_date +
                timedelta(days=random.randint(1, 10)),
                status=random.choice(status_choices),
            )

    def generate_medical_staff(self, count=10):
        """Generate fake medical staff"""
        departments = list(Department.objects.all())
        roles = [role[0] for role in MedicalStaff.STAFF_ROLES]

        for _ in range(count):
            MedicalStaff.objects.create(
                name=fake.name(),
                role=random.choice(roles),
                department=random.choice(departments),
                contact_number=fake.phone_number(),
                email=fake.email(),
                is_active=fake.boolean(),
            )
