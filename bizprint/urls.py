from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include(('products.urls', 'products'), namespace='products')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('designs/', include(('designs.urls', 'designs'), namespace='designs')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'bizprint.views.handler404'
handler500 = 'bizprint.views.handler500'
handler403 = 'bizprint.views.handler403'
handler400 = 'bizprint.views.handler400'
