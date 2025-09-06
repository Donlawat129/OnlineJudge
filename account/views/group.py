# account/views/group.py
from django.db import transaction
from django.db.models import Count
from utils.api import APIView, validate_serializer
from ..decorators import super_admin_required
from ..models import User, Group, UserGroup
from ..serializers import (
    GroupCreateSerializer,
    AssignUsersToGroupSerializer,
)

class GroupAdminAPI(APIView):
    """
    GET  /admin/groups        -> รายชื่อกลุ่มทั้งหมด
    POST /admin/groups        -> สร้างกลุ่มใหม่ (name)
    """
    @super_admin_required
    def get(self, request):
        qs = Group.objects.all().annotate(user_count=Count('usergroup'))
        data = [{"id": g.id, "name": g.name, "user_count": g.user_count} for g in qs.order_by("name")]
        return self.success(data)

    @validate_serializer(GroupCreateSerializer)
    @super_admin_required
    def post(self, request):
        name = request.data["name"].strip()
        group, _ = Group.objects.get_or_create(name=name)
        return self.success({"id": group.id, "name": group.name})

class AssignUsersToGroupAPI(APIView):
    """
    POST /admin/groups/assign
    body: {user_ids: [..], group_name: "A1", replace_existing: false}
    """
    @validate_serializer(AssignUsersToGroupSerializer)
    @super_admin_required
    def post(self, request):
        user_ids = request.data["user_ids"]
        group_name = request.data["group_name"].strip()
        replace_existing = request.data.get("replace_existing", False)

        with transaction.atomic():
            group, _ = Group.objects.get_or_create(name=group_name)

            if replace_existing:
                UserGroup.objects.filter(user_id__in=user_ids).delete()

            # กันซ้ำ
            existed = set(
                UserGroup.objects.filter(user_id__in=user_ids, group=group)
                .values_list("user_id", flat=True)
            )
            to_create = [UserGroup(user_id=uid, group=group) for uid in user_ids if uid not in existed]
            if to_create:
                UserGroup.objects.bulk_create(to_create)
        return self.success()

class RemoveUsersFromGroupAPI(APIView):
    """
    POST /admin/groups/remove
    body: {user_ids: [..], group_name: "A1"}
    """
    @validate_serializer(AssignUsersToGroupSerializer)  # reuse fields user_ids + group_name
    @super_admin_required
    def post(self, request):
        user_ids = request.data["user_ids"]
        group_name = request.data["group_name"].strip()
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return self.success()  # ไม่มีอยู่แล้ว ถือว่าลบสำเร็จ

        UserGroup.objects.filter(user_id__in=user_ids, group=group).delete()
        return self.success()

class ClearUsersGroupsAPI(APIView):
    """
    POST /admin/groups/clear
    body: {user_ids: [..]}
    """
    @super_admin_required
    def post(self, request):
        user_ids = request.data.get("user_ids") or []
        if not isinstance(user_ids, list) or not user_ids:
            return self.error("user_ids is required and must be a non-empty list")
        UserGroup.objects.filter(user_id__in=user_ids).delete()
        return self.success()
