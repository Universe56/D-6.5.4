from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

urlpatterns = [
   path('admin/', admin.site.urls),
   path('pages/', include('django.contrib.flatpages.urls')),
   path('news/', include('news.urls')),
   path('articles/', include('news.urls')),
   path('', include('protect.urls')),
   path('sign/', include('sign.urls')),
   path('accounts/', include('allauth.urls')),
   path('appointments/', include(('appointments.urls', 'appointments'), namespace='appointments')),
]
