from django.contrib import admin
from .models import Record

class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'apply_time', 'start_time', 'end_time')

admin.site.register(Record, RecordAdmin)