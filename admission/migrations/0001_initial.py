# Generated by Django 5.1.5 on 2025-02-02 22:35

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bed",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("bed_number", models.CharField(max_length=10)),
                (
                    "bed_type",
                    models.CharField(
                        choices=[
                            ("standard", "Standard"),
                            ("electric", "Electric"),
                            ("bariatric", "Bariatric"),
                            ("icu_special", "ICU Special"),
                        ],
                        max_length=15,
                    ),
                ),
                ("is_available", models.BooleanField(default=True)),
                ("is_operational", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="PackageService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("is_mandatory", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("age", models.PositiveSmallIntegerField()),
                (
                    "gender",
                    models.CharField(
                        choices=[
                            ("male", "Male"),
                            ("female", "Female"),
                            ("other", "Other"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "contact_number",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                regex="^\\+?1?\\d{9,15}$"
                            )
                        ],
                    ),
                ),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("address", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="TreatmentPackage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Admission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("admission_date", models.DateTimeField()),
                ("discharge_date", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("admitted", "Admitted"),
                            ("discharged", "Discharged"),
                            ("transferred", "Transferred"),
                        ],
                        default="admitted",
                        max_length=20,
                    ),
                ),
                (
                    "bed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="admission.bed"
                    ),
                ),
                (
                    "patient",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.patient",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BedMaintenance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("maintenance_date", models.DateField()),
                ("maintenance_type", models.CharField(max_length=50)),
                ("description", models.TextField()),
                ("performed_by", models.CharField(max_length=100)),
                ("next_maintenance_due", models.DateField()),
                (
                    "bed",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_records",
                        to="admission.bed",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Billing",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("partial", "Partial"),
                            ("completed", "Completed"),
                            ("insurance", "Insurance Processing"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("generated_date", models.DateTimeField()),
                ("due_date", models.DateTimeField()),
                (
                    "admission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bills",
                        to="admission.admission",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InsuranceClaim",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("insurance_provider", models.CharField(max_length=100)),
                ("policy_number", models.CharField(max_length=100)),
                ("claim_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("claim_date", models.DateTimeField()),
                ("status", models.CharField(max_length=20)),
                (
                    "settled_amount",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "bill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="insurance_claims",
                        to="admission.billing",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MedicalStaff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("doctor", "Doctor"),
                            ("nurse", "Nurse"),
                            ("technician", "Technician"),
                            ("administrator", "Administrator"),
                        ],
                        max_length=20,
                    ),
                ),
                ("contact_number", models.CharField(max_length=20)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.department",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdmissionVitals",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("recorded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "temperature",
                    models.DecimalField(decimal_places=1, max_digits=4, null=True),
                ),
                ("blood_pressure_systolic", models.IntegerField(null=True)),
                ("blood_pressure_diastolic", models.IntegerField(null=True)),
                ("pulse_rate", models.IntegerField(null=True)),
                ("respiratory_rate", models.IntegerField(null=True)),
                ("oxygen_saturation", models.IntegerField(null=True)),
                (
                    "admission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vitals",
                        to="admission.admission",
                    ),
                ),
                (
                    "recorded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdmissionDiagnosis",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("diagnosis", models.TextField()),
                ("diagnosis_date", models.DateTimeField()),
                ("notes", models.TextField(blank=True)),
                (
                    "admission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="diagnoses",
                        to="admission.admission",
                    ),
                ),
                (
                    "diagnosed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AdmissionService",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("status", models.CharField(default="scheduled", max_length=20)),
                ("scheduled_date", models.DateTimeField()),
                ("completed_date", models.DateTimeField(blank=True, null=True)),
                (
                    "admission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="services",
                        to="admission.admission",
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
                (
                    "service",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.packageservice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatientEmergencyContact",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("relationship", models.CharField(max_length=50)),
                ("contact_number", models.CharField(max_length=20)),
                ("address", models.TextField()),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emergency_contacts",
                        to="admission.patient",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PatientMedicalProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("blood_group", models.CharField(max_length=3)),
                ("allergies", models.TextField(blank=True)),
                ("medical_history", models.TextField(blank=True)),
                ("chronic_conditions", models.TextField(blank=True)),
                ("current_medications", models.TextField(blank=True)),
                (
                    "patient",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="medical_profile",
                        to="admission.patient",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_date", models.DateTimeField()),
                (
                    "payment_method",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("card", "Card"),
                            ("insurance", "Insurance"),
                            ("online", "Online Transfer"),
                        ],
                        max_length=20,
                    ),
                ),
                ("transaction_id", models.CharField(blank=True, max_length=100)),
                (
                    "bill",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="admission.billing",
                    ),
                ),
                (
                    "received_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("room_number", models.CharField(max_length=10, unique=True)),
                (
                    "room_type",
                    models.CharField(
                        choices=[
                            ("general_ac", "General AC"),
                            ("general_non_ac", "General Non AC"),
                            ("icu_1", "ICU 1"),
                            ("icu_2", "ICU 2"),
                            ("icu_3", "ICU 3"),
                            ("emergency", "Emergency"),
                        ],
                        max_length=15,
                    ),
                ),
                ("floor", models.PositiveSmallIntegerField()),
                ("is_operational", models.BooleanField(default=True)),
                ("capacity", models.PositiveSmallIntegerField(default=1)),
                (
                    "department",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.department",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="bed",
            name="room",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="beds",
                to="admission.room",
            ),
        ),
        migrations.CreateModel(
            name="RoomFacility",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("has_ventilator", models.BooleanField(default=False)),
                ("has_oxygen", models.BooleanField(default=False)),
                ("has_suction", models.BooleanField(default=False)),
                ("has_cardiac_monitor", models.BooleanField(default=False)),
                ("has_defibrillator", models.BooleanField(default=False)),
                (
                    "room",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facilities",
                        to="admission.room",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StaffProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("qualification", models.CharField(max_length=255)),
                ("license_number", models.CharField(max_length=50, unique=True)),
                ("specialization", models.CharField(max_length=100)),
                ("experience_years", models.PositiveIntegerField()),
                ("joining_date", models.DateField()),
                (
                    "staff",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to="admission.medicalstaff",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="packageservice",
            name="package",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="services",
                to="admission.treatmentpackage",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="bed",
            unique_together={("room", "bed_number")},
        ),
    ]
