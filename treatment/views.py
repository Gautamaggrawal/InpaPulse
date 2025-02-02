from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from admission.models import Admission, MedicalStaff
from .models import Treatment, Medication
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from datetime import datetime
from .models import *
from .forms import TreatmentForm, MedicationForm
from admission.models import Patient
from django.views import View


class AdmissionTreatmentListView(ListView):
    model = Treatment
    template_name = 'treatment/patient_treatment_list.html'
    context_object_name = 'treatments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Treatment.objects.select_related(
            'admission__patient',
            'performed_by'
        ).prefetch_related(
            'medications'
        )

        # Filter by patient name
        patient_name = self.request.GET.get('patient_name')
        if patient_name:
            queryset = queryset.filter(
                Q(admission__patient__name__icontains=patient_name)
            )

        admission_id = self.request.GET.get('admission_id')
        if admission_id:
            queryset = queryset.filter(
                Q(admission_id=admission_id)
            )

        # Filter by date range
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                queryset = queryset.filter(treatment_date__gte=start_date)
            except ValueError:
                pass

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
                queryset = queryset.filter(treatment_date__lte=end_date)
            except ValueError:
                pass

        return queryset.order_by('-treatment_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'patient_name': self.request.GET.get('patient_name', ''),
            'start_date': self.request.GET.get('start_date', ''),
            'end_date': self.request.GET.get('end_date', ''),
        })
        return context


class TreatmentDetailView(DetailView):
    model = Treatment
    template_name = 'treatment_detail.html'
    context_object_name = 'treatment'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medications'] = self.object.medications.all()
        return context


def add_medication(request, treatment_id):
    treatment = get_object_or_404(Treatment, id=treatment_id)
    if request.method == 'POST':
        medicine_name = request.POST['medicine_name']
        dosage = request.POST['dosage']
        route = request.POST['route']
        given_by = request.POST['given_by']

        medical_staff = get_object_or_404(MedicalStaff, id=given_by)

        medication = Medication.objects.create(
            treatment=treatment,
            medicine_name=medicine_name,
            dosage=dosage,
            route=route,
            given_by=medical_staff
        )
        return redirect('treatment_detail', pk=treatment.id)

    medical_staff = MedicalStaff.objects.all()
    return render(request, 'add_medication.html', {'treatment': treatment, 'medical_staff': medical_staff})


class TreatmentAndMedicationView(View):
    template_name = 'treatment/treatment_and_medication.html'

    def get(self, request, pk):
        admission = Admission.objects.get(pk=pk)
        treatment_form = TreatmentForm()
        medication_form = MedicationForm()
        return render(request, self.template_name, {
            'admission': admission,
            'treatment_form': treatment_form,
            'medication_form': medication_form
        })

    def post(self, request, pk):
        admission = Admission.objects.get(pk=pk)
        treatment_form = TreatmentForm(request.POST)
        medication_form = MedicationForm(request.POST)

        if treatment_form.is_valid() and medication_form.is_valid():
            treatment = treatment_form.save(commit=False)
            treatment.admission = admission
            treatment.save()

            medication = medication_form.save(commit=False)
            medication.patient = admission
            medication.treatment = treatment
            medication.save()

            return redirect('admission_detail', pk=pk)

        return render(request, self.template_name, {
            'admission': admission,
            'treatment_form': treatment_form,
            'medication_form': medication_form
        })
