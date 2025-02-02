from django.urls import path, include
from . import views

# API endpoints
api_patterns = [
    path('get-available-beds/', views.get_available_beds,
         name='get_available_beds'),
    path('get-room-availability/', views.get_room_availability,
         name='get_room_availability'),
]

# Admission related patterns
admission_patterns = [
    path('<int:pk>/', views.AdmissionDetailView.as_view(), name='admission_detail'),
    path('<int:pk>/edit/', views.AdmissionUpdateView.as_view(),
         name='admission_edit'),
    path('<int:admission_id>/vitals/create/',
         views.AdmissionVitalsCreateView.as_view(),
         name='admission_vitals_create'),
    path('<int:admission_id>/diagnoses/create/',
         views.AdmissionDiagnosisCreateView.as_view(),
         name='admission_diagnoses_create'),
]

urlpatterns = [
    # Main views
    path('', views.RoomAllocationListView.as_view(), name='room_allocation_list'),
    path('admit/', views.AdmissionCreateView.as_view(), name='admit_patient'),
    path('patient/<int:pk>/', views.PatientUpdateView.as_view(),
         name='patient_detail'),

    # Include admission patterns
    path('admission/', include(admission_patterns)),

    # Include API patterns
    path('api/', include(api_patterns)),
]
