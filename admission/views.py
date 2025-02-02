from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime
from .models import Admission, Room, Bed, Patient
from .forms import (
    AdmissionForm,
    AdmissionVitalsCreateForm,
    AdmissionDiagnosisCreateForm
)

# Mixin for common admission-related functionality


class AdmissionQuerysetMixin:
    def get_queryset(self):
        return Admission.objects.select_related(
            'patient',
            'bed',
            'bed__room',
            'bed__room__department'
        )


class BaseAdmissionView(LoginRequiredMixin, AdmissionQuerysetMixin):
    model = Admission
    context_object_name = 'admission'


class RoomAllocationListView(BaseAdmissionView, ListView):
    template_name = 'admission/room_allocation_list.html'
    context_object_name = 'allocations'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-admission_date')
        filters = {}

        # Get filter parameters
        status = self.request.GET.get('admission_status', 'admitted')
        patient_name = self.request.GET.get('patient_name')
        date_filter = self.request.GET.get('admission_date')
        department = self.request.GET.get('department')
        discharge_date = self.request.GET.get('discharge_date')

        # Apply filters
        if status:
            if status == "All Statuses...":
                filters['status'] = 'admitted'
            else:
                filters['status'] = status
        if patient_name:
            filters['patient__name__icontains'] = patient_name
        if department:
            filters['bed__room__department_id'] = department
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                filters['admission_date__date'] = filter_date
            except ValueError:
                pass
        if discharge_date:
            try:
                discharge_date = datetime.strptime(
                    discharge_date, '%Y-%m-%d').date()
                filters['discharge_date__date'] = discharge_date
            except ValueError:
                pass

        return queryset.filter(**filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'current_time': timezone.now(),
            'total_rooms': Room.objects.count(),
            'occupied_rooms': Room.objects.filter(
                beds__admission__status='admitted'
            ).distinct().count()
        })
        return context


class AdmissionDetailView(BaseAdmissionView, DetailView):
    template_name = 'admission/admission_detail.html'

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'diagnoses',
            'vitals',
            'services'
        )


class AdmissionUpdateView(BaseAdmissionView, UpdateView):
    template_name = 'admission/admission_edit.html'
    fields = ['patient', 'bed', 'admission_date', 'discharge_date', 'status']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Make specific fields read-only
        for field in ['patient', 'bed']:
            form.fields[field].widget.attrs['readonly'] = True
        return form

    def get_success_url(self):
        return reverse_lazy('admission_detail', kwargs={'pk': self.object.pk})


class AdmissionCreateView(LoginRequiredMixin, CreateView):
    form_class = AdmissionForm
    template_name = 'admission/admit_patient.html'
    success_url = reverse_lazy('room_allocation_list')


class BaseRecordCreateView(LoginRequiredMixin, CreateView):
    template_name = None
    form_class = None

    def get_initial(self):
        admission_id = self.kwargs.get('admission_id')
        return {'admission': admission_id}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admission_id = self.kwargs.get('admission_id')
        context['admission'] = get_object_or_404(Admission, id=admission_id)
        return context

    def form_valid(self, form):
        form.instance.admission_id = self.kwargs.get('admission_id')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('admission_detail', kwargs={'pk': self.kwargs['admission_id']})


class AdmissionVitalsCreateView(BaseRecordCreateView):
    template_name = 'admission/admission_vitals.html'
    form_class = AdmissionVitalsCreateForm


class AdmissionDiagnosisCreateView(BaseRecordCreateView):
    template_name = 'admission/admission_diagnoses.html'
    form_class = AdmissionDiagnosisCreateForm


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    template_name = 'admission/patient_edit.html'
    fields = '__all__'
    context_object_name = 'patient'

    def get_success_url(self):
        return reverse_lazy('admission_detail', kwargs={
            'pk': self.object.admission_set.first().pk
        })

# AJAX views


def get_available_beds(request):
    room_id = request.GET.get('room_id')
    if room_id:
        beds = Bed.objects.filter(
            room_id=room_id,
            is_available=True
        ).values('id', 'bed_number', 'bed_type')
        return JsonResponse({'beds': list(beds)})
    return JsonResponse({'beds': []})


def get_room_availability(request):
    filters = {'is_operational': True}

    if room_type := request.GET.get('room_type'):
        filters['room_type'] = room_type
    if floor := request.GET.get('floor'):
        filters['floor'] = floor

    availability = Room.objects.filter(
        **filters,
        beds__is_available=True
    ).values('floor').annotate(
        available_beds=Count('beds', filter=Q(beds__is_available=True))
    )

    return JsonResponse({'availability': list(availability)})
