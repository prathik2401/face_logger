from django.contrib import admin
from .models import Person, VisitLog

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'visit_count', 'last_seen', 'created_at')
    search_fields = ('name', 'id')

@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ('person', 'timestamp')
    list_filter = ('timestamp',)
