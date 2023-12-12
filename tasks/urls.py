from django.urls import path
from . import views


urlpatterns = [
    path('tasks/', views.ListCreateTaskView.as_view(), name='list_create_task'),
    path('tasks/<int:pk>/', views.RetrieveUpdateDestroyTaskView.as_view(), name='retrieve_update_toggle_task'),
]