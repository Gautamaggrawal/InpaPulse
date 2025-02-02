from django.db import models
from django.utils import timezone
from admission.models import Admission, MedicalStaff

class Treatment(models.Model):
    """Model for tracking patient treatments"""
    admission = models.ForeignKey(Admission, on_delete=models.CASCADE, related_name='treatments')
    treatment_date = models.DateTimeField(default=timezone.now)
    treatment_type = models.CharField(max_length=100)
    description = models.TextField()
    performed_by = models.ForeignKey(MedicalStaff, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-treatment_date']

    def __str__(self):
        return f"{self.admission.patient.name} - {self.treatment_type} ({self.treatment_date})"

class Medication(models.Model):
    """Model for tracking medications given to patients"""
    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('iv', 'Intravenous'),
        ('im', 'Intramuscular'),
        ('sc', 'Subcutaneous'),
        ('other', 'Other'),
    ]
    
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='medications')
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES)
    given_at = models.DateTimeField(default=timezone.now)
    given_by = models.ForeignKey(MedicalStaff, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-given_at']

    def __str__(self):
        return f"{self.medicine_name} - {self.dosage}"