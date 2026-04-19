from django.contrib import admin
from .models import File

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'file_type', 'uploaded_by', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('file', 'uploaded_by__email')
    readonly_fields = ('created_at', 'updated_at')
