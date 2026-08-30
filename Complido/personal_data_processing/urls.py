from django.urls import path
from .views import (
    processings_list,
    processing_detail,
    processing_create,
    processing_update,
    processing_delete
    )

app_name = "personal_data_processing"

urlpatterns = [
    path("", processings_list, name="processings_list"),
    path("<int:id>/", processing_detail, name="processing_detail"),
    path("create", processing_create, name="processing_create"),
    path("<int:id>/update/", processing_update, name="processing_update"),
    path("<int:id>/delete/", processing_delete, name="processing_delete"),
]