from .models import AdmissionDiagnosis
from django import forms
from django.utils import timezone
from .models import (Admission, Patient, Room, Bed, MedicalStaff,
                     TreatmentPackage, Billing, AdmissionService, Payment,
                     AdmissionVitals
                     )


class AdmissionForm(forms.ModelForm):
    assignment_type = forms.ChoiceField(
        choices=[('auto', 'Automatic'), ('manual', 'Manual')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='auto'
    )

    # Automatic assignment fields
    room_type = forms.ChoiceField(
        choices=Room.ROOM_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    preferred_floor = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Manual assignment fields
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_operational=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bed = forms.ModelChoiceField(
        queryset=Bed.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Patient information
    name = forms.CharField(max_length=255, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    age = forms.IntegerField(widget=forms.NumberInput(
        attrs={'class': 'form-control'}))
    gender = forms.ChoiceField(
        choices=Patient.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    attendant = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3}))
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    admission_time = forms.TimeField(widget=forms.TimeInput(
        attrs={'class': 'form-control', 'type': 'time'}))
    admission_date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date'}))

    # Doctor and Staff
    doctor = forms.ModelChoiceField(
        queryset=MedicalStaff.objects.filter(role='doctor', is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    admission_by = forms.ModelChoiceField(
        queryset=MedicalStaff.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Billing and package selection
    total_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    advance_payment = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHODS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='cash'
    )
    balance_remaining = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly'
        })
    )
    service_package = forms.ModelChoiceField(
        queryset=TreatmentPackage.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Admission
        fields = ['admission_date', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set available rooms
        available_rooms = Room.objects.filter(
            is_operational=True, beds__is_available=True).distinct()
        self.fields['room'].queryset = available_rooms

        # Set available beds if room is selected
        if 'room' in self.data:
            try:
                room_id = int(self.data.get('room'))
                self.fields['bed'].queryset = Bed.objects.filter(
                    room_id=room_id, is_available=True)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['bed'].queryset = self.instance.bed.room.beds.filter(
                is_available=True)

    def clean(self):
        cleaned_data = super().clean()
        assignment_type = cleaned_data.get('assignment_type')

        if assignment_type == 'auto':
            room_type = cleaned_data.get('room_type')
            if not room_type:
                raise forms.ValidationError(
                    "Room type is required for automatic assignment")
        else:
            room = cleaned_data.get('room')
            bed = cleaned_data.get('bed')

            if not room:
                raise forms.ValidationError(
                    "Room selection is required for manual assignment")
            if not bed:
                raise forms.ValidationError(
                    "Bed selection is required for manual assignment")
            if not bed.is_available:
                raise forms.ValidationError("Selected bed is not available")
            if bed.room != room:
                raise forms.ValidationError(
                    "Selected bed does not belong to the selected room")

        # Validate payment details
        total_amount = cleaned_data.get('total_amount')
        advance_payment = cleaned_data.get('advance_payment')
        if total_amount and advance_payment and advance_payment > total_amount:
            raise forms.ValidationError(
                "Advance payment cannot be greater than total amount")
        cleaned_data['balance_remaining'] = total_amount - advance_payment

        return cleaned_data

    def get_available_bed(self):
        """Find an available bed based on room type and floor preference"""
        room_type = self.cleaned_data.get('room_type')
        preferred_floor = self.cleaned_data.get('preferred_floor')

        beds_query = Bed.objects.filter(
            is_available=True,
            # is_operational=True,
            # room__is_operational=True,
            room__room_type=room_type
        )

        if preferred_floor is not None:
            beds_query = beds_query.filter(room__floor=preferred_floor)

        beds_query = beds_query.order_by('room__floor', 'bed_number')
        return beds_query.first()

    def save(self, commit=True):
        # Create or update patient
        patient, _ = Patient.objects.update_or_create(
            name=self.cleaned_data['name'],
            defaults={
                'gender': self.cleaned_data['gender'],
                'contact_number': self.cleaned_data['mobile'],
                'address': self.cleaned_data['address'],
                'age': self.cleaned_data['age'],
            }
        )

        # Determine bed based on assignment type
        if self.cleaned_data['assignment_type'] == 'auto':
            bed = self.get_available_bed()
            if not bed:
                raise forms.ValidationError(
                    "No available beds found matching the criteria")
        else:
            bed = self.cleaned_data['bed']

        # Create the admission instance
        admission = super().save(commit=False)
        admission.patient = patient
        admission.bed = bed
        admission.doctor = self.cleaned_data['doctor']
        admission.admission_by = self.cleaned_data['admission_by']

        if commit:
            admission.save()

            # Mark the bed as occupied
            bed.is_available = False
            bed.save()

            # Generate a billing record
            bill = Billing.objects.create(
                admission=admission,
                total_amount=self.cleaned_data['total_amount'],
                payment_status='pending',
                generated_date=timezone.now(),
                due_date=timezone.now() + timezone.timedelta(days=30)
            )

            # Create payment record if advance payment is made
            if self.cleaned_data['advance_payment'] > 0:
                Payment.objects.create(
                    bill=bill,
                    amount=self.cleaned_data['advance_payment'],
                    payment_date=timezone.now(),
                    payment_method=self.cleaned_data['payment_method'],
                    received_by=self.cleaned_data['admission_by']
                )

            # Assign services if a package is selected
            if self.cleaned_data['service_package']:
                for service in self.cleaned_data['service_package'].services.all():
                    AdmissionService.objects.create(
                        admission=admission,
                        service=service,
                        status='scheduled',
                        scheduled_date=timezone.now()
                    )

        return admission


class AdmissionVitalsCreateForm(forms.ModelForm):
    """Form to create vitals for a specific admission"""

    class Meta:
        model = AdmissionVitals
        fields = ['temperature', 'blood_pressure_systolic',
                  'blood_pressure_diastolic',
                  'pulse_rate',
                  'respiratory_rate',
                  'oxygen_saturation',
                  'recorded_by']

    # Hidden field for admission ID
    admission = forms.IntegerField(widget=forms.HiddenInput())
    recorded_at = forms.DateTimeField(
        initial=timezone.now, widget=forms.HiddenInput())

    def clean_admission(self):
        admission_id = self.cleaned_data.get('admission')
        try:
            admission = Admission.objects.get(id=admission_id)
        except Admission.DoesNotExist:
            raise forms.ValidationError('Admission not found')
        return admission


class AdmissionDiagnosisCreateForm(forms.ModelForm):
    """Form to create a diagnosis for a specific admission"""

    class Meta:
        model = AdmissionDiagnosis
        fields = ['diagnosis', 'diagnosed_by', 'diagnosis_date', 'notes']

    # Hidden field for admission ID
    admission = forms.IntegerField(widget=forms.HiddenInput())
    diagnosis_date = forms.DateTimeField(
        initial=timezone.now, widget=forms.HiddenInput())

    def clean_admission(self):
        admission_id = self.cleaned_data.get('admission')
        try:
            admission = Admission.objects.get(id=admission_id)
        except Admission.DoesNotExist:
            raise forms.ValidationError('Admission not found')
        return admission
