from django.contrib import admin
from .models import Todo

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'completed', 'due_date', 'created_at')
    list_filter = ('completed', 'created_at', 'due_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Task Details', {
            'fields': ('title', 'description', 'completed')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at')
        }),
    )
