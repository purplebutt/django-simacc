from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('secure_login/', admin.site.urls),
    # path('admin/', include('category.urls', namespace='category')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls', namespace="accounts")),
    path('accounting/', include('accounting.urls', namespace="accounting")),
    path('', include('cover.urls', namespace='cover')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
