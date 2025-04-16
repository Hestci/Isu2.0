from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from isu.myapp import views as myapp_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('', include('isu.myapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 