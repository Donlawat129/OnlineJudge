from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import CreateOrEditProblemSerializer

class ProblemTagAPI(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateOrEditProblemSerializer(data=request.data)

        # Validate data
        if serializer.is_valid():
            # ดึง tag ที่ผู้ใช้ส่งมา
            tag_names = request.data.get('tags', [])

            # ใช้ serializer ในการสร้าง tag
            tags = serializer.create_or_edit_tags(tag_names)

            # ส่ง response กลับไปให้ผู้ใช้
            return Response({"tags": [tag.name for tag in tags]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
