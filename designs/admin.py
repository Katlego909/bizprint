from django.contrib import admin
from .models import DesignPackage, DesignRequest
from import_export.admin import ImportExportModelAdmin


@admin.register(DesignPackage)
class DesignPackageAdmin(ImportExportModelAdmin):
    list_display = ('title', 'price')

@admin.register(DesignRequest)
class DesignRequestAdmin(ImportExportModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email',)
