from django.contrib import admin
from .models import CustomerProfile, NewsletterSubscriber
from import_export.admin import ImportExportModelAdmin

admin.site.register(CustomerProfile, ImportExportModelAdmin)
admin.site.register(NewsletterSubscriber, ImportExportModelAdmin)
