from django.urls import path
from .views import GroupsListView, hello_world_view

app_name = "myapiname"

urlpatterns = [
    path("hello/", hello_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
]
