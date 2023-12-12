from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from tasks.models import Task
from tasks.serializers import TaskSerializer
import datetime


class ListCreateTaskView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Task.objects.all()
        user = self.request.query_params.get('user', None)
        queryset = queryset.filter(user=user)
        queryset = queryset.filter(deadline__gt=datetime.datetime.now())
        queryset = queryset.filter(finished=False)

        return queryset
    

class RetrieveUpdateDestroyTaskView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.query_params.get('user', None)
        instance = self.get_object()

        if str(instance.user) != str(user):
            raise PermissionDenied("Permission denied.")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    

    def perform_update(self, serializer):
        user = self.request.query_params.get('user', None)
        instance = self.get_object()

        if str(instance.user) != str(user):
            raise PermissionDenied("Permission denied.")

        serializer.save()

    
    def delete(self, request, *args, **kwargs):
        user = self.request.query_params.get('user', None)
        instance = self.get_object()

        if str(instance.user) != str(user):
            raise PermissionDenied("Permission denied.")

        instance.finished = not instance.finished
        instance.save()

        serializer = self.get_serializer(instance)

        return Response(serializer.data)