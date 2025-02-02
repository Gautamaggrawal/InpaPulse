from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Bed)
admin.site.register(Patient)
admin.site.register(Admission)
admin.site.register(Room)
admin.site.register(AdmissionVitals)
