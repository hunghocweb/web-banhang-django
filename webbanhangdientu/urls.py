from django.urls import path, include
from app.admin import admin_site  # Sử dụng admin_site tùy chỉnh

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', include('app.urls'))
]


