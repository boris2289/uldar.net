# Django imports
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", view = include('apps.tags.urls')),
    path("api/", view = include('apps.questions.urls')),
    path("api/v1/users/", include("apps.users.urls")),

    path("api/", include("apps.users.urls")),
]