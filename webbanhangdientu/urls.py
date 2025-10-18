from django.urls import path, include
from app.admin import admin_site  # Sử dụng admin_site tùy chỉnh

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('app.urls'))
]

urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)