from django.contrib import admin
from django.urls import path,include
# this 2 things for configure media ans static for urls
from django.conf import settings
from django.conf.urls.static import static
from authapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('ekartapp.urls')),
    path('auth/',include('authapp.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



