from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department, RoomFacility, Bed, Room, PackageService,
    PatientMedicalProfile, Patient, AdmissionVitals, Admission,
    AdmissionDiagnosis, TreatmentPackage, StaffProfile, MedicalStaff,
    BedMaintenance, PatientEmergencyContact, Billing, AdmissionService,
    Payment, InsuranceClaim)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_room_count', 'get_staff_count', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

    def get_room_count(self, obj):
        return obj.room_set.count()
    get_room_count.short_description = 'Rooms'

    def get_staff_count(self, obj):
        return obj.medicalstaff_set.count()
    get_staff_count.short_description = 'Staff'


class RoomFacilityInline(admin.StackedInline):
    model = RoomFacility
    can_delete = False


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    show_change_link = True


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'department', 'room_type', 'floor',
                    'is_operational', 'capacity', 'available_beds')
    list_filter = ('department', 'room_type', 'floor', 'is_operational')
    search_fields = ('room_number', 'department__name')
    inlines = [RoomFacilityInline, BedInline]

    def available_beds(self, obj):
        available = obj.beds.filter(is_available=True).count()
        total = obj.beds.count()
        return f"{available}/{total}"
    available_beds.short_description = 'Available Beds'


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bed_type', 'is_available', 'is_operational',
                    'get_current_patient')
    list_filter = ('bed_type', 'is_available',
                   'is_operational', 'room__department')
    search_fields = ('bed_number', 'room__room_number')

    def get_current_patient(self, obj):
        current_admission = Admission.objects.filter(
            bed=obj, status='admitted').first()
        if current_admission:
            return current_admission.patient.name
        return '-'
    get_current_patient.short_description = 'Current Patient'


class PatientMedicalProfileInline(admin.StackedInline):
    model = PatientMedicalProfile
    can_delete = False


class PatientEmergencyContactInline(admin.TabularInline):
    model = PatientEmergencyContact
    extra = 1


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'contact_number', 'email',
                    'get_admission_status')
    list_filter = ('gender', 'medical_profile__blood_group')
    search_fields = ('name', 'contact_number', 'email')
    inlines = [PatientMedicalProfileInline, PatientEmergencyContactInline]

    def get_admission_status(self, obj):
        try:
            admission = obj.admission
            status = admission.get_status_display()
            return format_html(
                '<span style="color: {};">{}</span>',
                {'admitted': 'green', 'discharged': 'red',
                 'transferred': 'orange'}[admission.status],
                status
            )
        except Admission.DoesNotExist:
            return '-'
    get_admission_status.short_description = 'Admission Status'


class AdmissionDiagnosisInline(admin.TabularInline):
    model = AdmissionDiagnosis
    extra = 1


class AdmissionVitalsInline(admin.TabularInline):
    model = AdmissionVitals
    extra = 0
    show_change_link = True


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'bed', 'admission_date', 'status',
                    'get_days_admitted', 'get_billing_status')
    list_filter = ('status', 'bed__room__department')
    search_fields = ('patient__name', 'bed__room__room_number')
    inlines = [AdmissionDiagnosisInline, AdmissionVitalsInline]
    raw_id_fields = ('patient', 'bed')

    def get_days_admitted(self, obj):
        if obj.discharge_date:
            delta = obj.discharge_date - obj.admission_date
        else:
            delta = date.today() - obj.admission_date.date()
        return f"{delta.days} days"
    get_days_admitted.short_description = 'Duration'

    def get_billing_status(self, obj):
        latest_bill = obj.bills.order_by('-generated_date').first()
        if latest_bill:
            return format_html(
                '<span style="color: {};">{}</span>',
                {'pending': 'red', 'partial': 'orange',
                 'completed': 'green', 'insurance': 'blue'}[latest_bill.payment_status],
                latest_bill.get_payment_status_display()
            )
        return '-'
    get_billing_status.short_description = 'Billing Status'


@admin.register(TreatmentPackage)
class TreatmentPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'get_services_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

    def get_services_count(self, obj):
        return obj.services.count()
    get_services_count.short_description = 'Services'


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False


@admin.register(MedicalStaff)
class MedicalStaffAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'department', 'email',
                    'get_experience_years', 'is_active')
    list_filter = ('role', 'department', 'is_active')
    search_fields = ('name', 'email', 'contact_number')
    inlines = [StaffProfileInline]

    def get_experience_years(self, obj):
        try:
            return f"{obj.profile.experience_years} years"
        except StaffProfile.DoesNotExist:
            return '-'
    get_experience_years.short_description = 'Experience'


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('admission', 'total_amount', 'payment_status',
                    'generated_date', 'due_date', 'get_paid_amount')
    list_filter = ('payment_status',)
    search_fields = ('admission__patient__name',)

    def get_paid_amount(self, obj):
        paid = sum(payment.amount for payment in obj.payments.all())
        return f"${paid:.2f} / ${obj.total_amount:.2f}"
    get_paid_amount.short_description = 'Paid Amount'


# Register remaining models with basic configuration
admin.site.register(RoomFacility)
admin.site.register(BedMaintenance)
admin.site.register(PatientMedicalProfile)
admin.site.register(PatientEmergencyContact)
admin.site.register(AdmissionService)
admin.site.register(Payment)
admin.site.register(InsuranceClaim)
admin.site.register(PackageService)
