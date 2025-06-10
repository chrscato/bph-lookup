from django.contrib import admin
from .models import State, Region, ProcedureCode, FeeSchedule, FeeScheduleRate

admin.site.register(State)
admin.site.register(Region)
admin.site.register(ProcedureCode)
admin.site.register(FeeSchedule)
admin.site.register(FeeScheduleRate) 