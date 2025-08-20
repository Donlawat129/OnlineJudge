class ProblemSerializer(BaseProblemSerializer):
    # ส่วนของ serializer อื่นๆ
    tags = TagSerializer(many=True)  # ใช้ serializer ที่ใช้จัดการ tag

    def create_or_edit_tags(self, tag_names):
        tags = []
        for name in tag_names:
            tag, created = ProblemTag.objects.get_or_create(name=name)
            tags.append(tag)
        return tags


class ProblemTagAPI(APIView):
    def post(self, request, *args, **kwargs):
        # ดึง tag ที่ผู้ใช้ส่งมา
        tag_names = request.data.get('tags', [])

        # สร้างหรือดึง tag ที่มีอยู่
        tags = []
        for name in tag_names:
            tag, created = ProblemTag.objects.get_or_create(name=name)  # ใช้ get_or_create เพื่อตรวจสอบ tag
            tags.append(tag)

        # ส่ง response กลับไปให้ผู้ใช้
        return Response({"tags": [tag.name for tag in tags]}, status=status.HTTP_201_CREATED)
