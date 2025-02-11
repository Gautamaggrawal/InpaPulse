# Generated by Django 5.1.5 on 2025-02-02 22:35

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("admission", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Treatment",
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
                (
                    "treatment_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("treatment_type", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("notes", models.TextField(blank=True)),
                (
                    "admission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="treatments",
                        to="admission.admission",
                    ),
                ),
                (
                    "performed_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
            ],
            options={
                "ordering": ["-treatment_date"],
            },
        ),
        migrations.CreateModel(
            name="Medication",
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
                ("medicine_name", models.CharField(max_length=100)),
                ("dosage", models.CharField(max_length=50)),
                (
                    "route",
                    models.CharField(
                        choices=[
                            ("oral", "Oral"),
                            ("iv", "Intravenous"),
                            ("im", "Intramuscular"),
                            ("sc", "Subcutaneous"),
                            ("other", "Other"),
                        ],
                        max_length=20,
                    ),
                ),
                ("given_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("notes", models.TextField(blank=True)),
                (
                    "given_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="admission.medicalstaff",
                    ),
                ),
                (
                    "treatment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="medications",
                        to="treatment.treatment",
                    ),
                ),
            ],
            options={
                "ordering": ["-given_at"],
            },
        ),
    ]
