from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

from .models import Problem
from .serializers import CreateProblemSerializer


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = CreateProblemSerializer

    @action(detail=False, methods=["post"])
    def create_problem(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # สร้าง Problem พร้อมกับ Tag ที่เลือกไว้
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
