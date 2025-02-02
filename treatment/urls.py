from .views import (TreatmentAndMedicationView, add_medication,
                    TreatmentDetailView, AdmissionTreatmentListView)
from django.urls import path

app_name = "treatment"

urlpatterns = [
    path('', AdmissionTreatmentListView.as_view(),
         name='admission_treatment_list'),
    path('<int:pk>/', TreatmentDetailView.as_view(),
         name='treatment_detail'),
    path('<int:treatment_id>/add-medication/',
         add_medication, name='add_medication'),
    path('patient/<int:pk>/treatment-and-medication/',
         TreatmentAndMedicationView.as_view(), name='treatment_and_medication'),
]
