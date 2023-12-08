from django.urls import path
from . import views


urlpatterns = [
    path('tasks/', views.ListCreateTaskView.as_view()),
    path('tasks/<int:pk>/', views.RetrieveUpdateDestroyTaskView.as_view()),
]