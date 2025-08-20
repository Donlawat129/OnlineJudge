from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from problem.models import ProblemTag
from .serializers import CreateOrEditProblemSerializer

class ProblemTagAPI(APIView):
    def post(self, request, *args, **kwargs):
        # ดึง tag ที่ผู้ใช้ส่งมา
        tag_names = request.data.get('tags', [])

        # สร้างหรือดึง tag ที่มีอยู่แล้ว
        tags = []
        for name in tag_names:
            # ใช้ get_or_create เพื่อตรวจสอบ tag ว่ามีอยู่แล้วหรือไม่
            tag, created = ProblemTag.objects.get_or_create(name=name)
            tags.append(tag)

        # ส่ง response กลับไปให้ผู้ใช้
        return Response({"tags": [tag.name for tag in tags]}, status=status.HTTP_201_CREATED)
