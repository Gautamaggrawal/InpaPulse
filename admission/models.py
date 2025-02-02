from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from datetime import date


class Department(models.Model):
    """Department model to organize hospital sections"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    """Room model with basic attributes"""
    ROOM_TYPES = [
        ('general_ac', 'General AC'),
        ('general_non_ac', 'General Non AC'),
        ('icu_1', 'ICU 1'),
        ('icu_2', 'ICU 2'),
        ('icu_3', 'ICU 3'),
        ('emergency', 'Emergency'),
    ]

    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=15, choices=ROOM_TYPES)
    floor = models.PositiveSmallIntegerField()
    is_operational = models.BooleanField(default=True)
    capacity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.room_number} ({self.get_room_type_display()})"


class RoomFacility(models.Model):
    """Separate model for room facilities"""
    room = models.OneToOneField(
        Room, on_delete=models.CASCADE, related_name='facilities')
    has_ventilator = models.BooleanField(default=False)
    has_oxygen = models.BooleanField(default=False)
    has_suction = models.BooleanField(default=False)
    has_cardiac_monitor = models.BooleanField(default=False)
    has_defibrillator = models.BooleanField(default=False)


class Bed(models.Model):
    """Bed model with basic attributes"""
    BED_TYPES = [
        ('standard', 'Standard'),
        ('electric', 'Electric'),
        ('bariatric', 'Bariatric'),
        ('icu_special', 'ICU Special'),
    ]

    room = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name='beds')
    bed_number = models.CharField(max_length=10)
    bed_type = models.CharField(max_length=15, choices=BED_TYPES)
    is_available = models.BooleanField(default=True)
    is_operational = models.BooleanField(default=True)

    class Meta:
        unique_together = ['room', 'bed_number']

    def __str__(self):
        return f"Room No: {self.room.room_number}, Bed No: {self.bed_number}"


class BedMaintenance(models.Model):
    """Separate model for bed maintenance tracking"""
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE,
                            related_name='maintenance_records')
    maintenance_date = models.DateField()
    maintenance_type = models.CharField(max_length=50)
    description = models.TextField()
    performed_by = models.CharField(max_length=100)
    next_maintenance_due = models.DateField()


class Patient(models.Model):
    """Patient model with basic information"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    contact_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    email = models.EmailField(blank=True)
    address = models.TextField()

    def __str__(self):
        return self.name


class PatientMedicalProfile(models.Model):
    """Separate model for patient medical information"""
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name='medical_profile')
    blood_group = models.CharField(max_length=3)
    allergies = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)


class PatientEmergencyContact(models.Model):
    """Separate model for emergency contacts"""
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=50)
    contact_number = models.CharField(max_length=20)
    address = models.TextField()


class Admission(models.Model):
    """Core admission model with minimal required fields"""
    STATUS_CHOICES = [
        ('admitted', 'Admitted'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    ]

    patient = models.OneToOneField(Patient, on_delete=models.PROTECT)
    bed = models.ForeignKey(Bed, on_delete=models.PROTECT)
    admission_date = models.DateTimeField()
    discharge_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='admitted')

    def __str__(self):
        return f"{self.patient.name} - {self.bed}"


class AdmissionDiagnosis(models.Model):
    """Separate model for diagnosis information"""
    admission = models.ForeignKey(
        Admission, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis = models.TextField()
    diagnosed_by = models.ForeignKey('MedicalStaff', on_delete=models.PROTECT)
    diagnosis_date = models.DateTimeField()
    notes = models.TextField(blank=True)


class AdmissionVitals(models.Model):
    """Separate model for patient vitals during admission"""
    admission = models.ForeignKey(
        Admission, on_delete=models.CASCADE, related_name='vitals')
    recorded_at = models.DateTimeField(auto_now_add=True)
    temperature = models.DecimalField(
        max_digits=4, decimal_places=1, null=True)
    blood_pressure_systolic = models.IntegerField(null=True)
    blood_pressure_diastolic = models.IntegerField(null=True)
    pulse_rate = models.IntegerField(null=True)
    respiratory_rate = models.IntegerField(null=True)
    oxygen_saturation = models.IntegerField(null=True)
    recorded_by = models.ForeignKey('MedicalStaff', on_delete=models.PROTECT)


class TreatmentPackage(models.Model):
    """Base package model"""
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PackageService(models.Model):
    """Services included in packages"""
    package = models.ForeignKey(
        TreatmentPackage, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=True)


class AdmissionService(models.Model):
    """Links admissions to services with tracking"""
    admission = models.ForeignKey(
        Admission, on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(PackageService, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, default='scheduled')
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(
        'MedicalStaff', on_delete=models.PROTECT, null=True)


class Billing(models.Model):
    """Separate billing model"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
        ('insurance', 'Insurance Processing'),
    ]

    admission = models.ForeignKey(
        Admission, on_delete=models.PROTECT, related_name='bills')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default='pending')
    generated_date = models.DateTimeField()
    due_date = models.DateTimeField()


class Payment(models.Model):
    """Separate model for payment tracking"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('insurance', 'Insurance'),
        ('online', 'Online Transfer'),
    ]

    bill = models.ForeignKey(
        Billing, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey('MedicalStaff', on_delete=models.PROTECT)


class InsuranceClaim(models.Model):
    """Separate insurance handling"""
    bill = models.ForeignKey(
        Billing, on_delete=models.PROTECT, related_name='insurance_claims')
    insurance_provider = models.CharField(max_length=100)
    policy_number = models.CharField(max_length=100)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claim_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    settled_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)


class MedicalStaff(models.Model):
    """Medical staff with basic information"""
    STAFF_ROLES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('technician', 'Technician'),
        ('administrator', 'Administrator'),
    ]

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=STAFF_ROLES)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.role}-{self.name}"


class StaffProfile(models.Model):
    """Separate model for detailed staff information"""
    staff = models.OneToOneField(
        MedicalStaff, on_delete=models.CASCADE, related_name='profile')
    qualification = models.CharField(max_length=255)
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField()
    joining_date = models.DateField()
