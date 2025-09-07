# account/views/admin.py
import os
import re
import xlsxwriter

from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password

from submission.models import Submission
from utils.api import APIView, validate_serializer
from utils.shortcuts import rand_str

from ..decorators import super_admin_required
from ..models import (
    AdminType, ProblemPermission, User, UserProfile, Group, UserGroup
)
from ..serializers import (
    EditUserSerializer, UserAdminSerializer, GenerateUserSerializer,
    ImportUserSeralizer, GroupSerializer, AssignUsersToGroupSerializer,
    BulkUsersSerializer
)

class UserAdminAPI(APIView):
    @validate_serializer(ImportUserSeralizer)
    @super_admin_required
    def post(self, request):
        data = request.data["users"]
        user_list = []
        for user_data in data:
            if len(user_data) != 4 or len(user_data[0]) > 32:
                return self.error(f"Error occurred while processing data '{user_data}'")
            user_list.append(User(
                username=user_data[0],
                password=make_password(user_data[1]),
                email=user_data[2]
            ))
        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create([
                    UserProfile(user=ret[i], real_name=data[i][3]) for i in range(len(ret))
                ])
            return self.success()
        except IntegrityError as e:
            return self.error(str(e).split("\n")[1])

    @validate_serializer(EditUserSerializer)
    @super_admin_required
    def put(self, request):
        data = request.data
        try:
            user = User.objects.get(id=data["id"])
        except User.DoesNotExist:
            return self.error("User does not exist")

        if User.objects.filter(username=data["username"].lower()).exclude(id=user.id).exists():
            return self.error("Username already exists")
        if User.objects.filter(email=data["email"].lower()).exclude(id=user.id).exists():
            return self.error("Email already exists")

        pre_username = user.username
        user.username = data["username"].lower()
        user.email = data["email"].lower()
        user.admin_type = data["admin_type"]
        user.is_disabled = data["is_disabled"]

        if data["admin_type"] == AdminType.ADMIN:
            user.problem_permission = data["problem_permission"]
        elif data["admin_type"] == AdminType.SUPER_ADMIN:
            user.problem_permission = ProblemPermission.ALL
        else:
            user.problem_permission = ProblemPermission.NONE

        if data["password"]:
            user.set_password(data["password"])

        if data["open_api"]:
            if not user.open_api:
                user.open_api_appkey = rand_str()
        else:
            user.open_api_appkey = None
        user.open_api = data["open_api"]

        if data["two_factor_auth"]:
            if not user.two_factor_auth:
                user.tfa_token = rand_str()
        else:
            user.tfa_token = None
        user.two_factor_auth = data["two_factor_auth"]

        user.save()
        if pre_username != user.username:
            Submission.objects.filter(username=pre_username).update(username=user.username)

        UserProfile.objects.filter(user=user).update(real_name=data["real_name"])
        return self.success(UserAdminSerializer(user).data)

    @super_admin_required
    def get(self, request):
        user_id = request.GET.get("id")
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.error("User does not exist")
            return self.success(UserAdminSerializer(user).data)

        qs = User.objects.all().order_by("-create_time")
        keyword = request.GET.get("keyword")
        if keyword:
            qs = qs.filter(
                Q(username__icontains=keyword) |
                Q(userprofile__real_name__icontains=keyword) |
                Q(email__icontains=keyword)
            )
        return self.success(self.paginate_data(request, qs, UserAdminSerializer))

    @super_admin_required
    def delete(self, request):
        ids = request.GET.get("ids")  # <-- ให้รับ ids ตรงกับ frontend
        if not ids:
            return self.error("Invalid Parameter, ids is required")
        id_list = ids.split(",")
        if str(request.user.id) in id_list:
            return self.error("Current user can not be deleted")
        User.objects.filter(id__in=id_list).delete()
        return self.success()


class GenerateUserAPI(APIView):
    @super_admin_required
    def get(self, request):
        file_id = request.GET.get("file_id")
        if not file_id:
            return self.error("Invalid Parameter, file_id is required")
        if not re.match(r"^[a-zA-Z0-9]+$", file_id):
            return self.error("Illegal file_id")
        file_path = f"/tmp/{file_id}.xlsx"
        if not os.path.isfile(file_path):
            return self.error("File does not exist")
        with open(file_path, "rb") as f:
            raw_data = f.read()
        os.remove(file_path)
        resp = HttpResponse(raw_data)
        resp["Content-Disposition"] = "attachment; filename=users.xlsx"
        resp["Content-Type"] = "application/xlsx"
        return resp

    @validate_serializer(GenerateUserSerializer)
    @super_admin_required
    def post(self, request):
        data = request.data
        number_max_length = max(len(str(data["number_from"])), len(str(data["number_to"])))
        if number_max_length + len(data["prefix"]) + len(data["suffix"]) > 32:
            return self.error("Username should not more than 32 characters")
        if data["number_from"] > data["number_to"]:
            return self.error("Start number must be lower than end number")

        file_id = rand_str(8)
        filename = f"/tmp/{file_id}.xlsx"
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("A:B", 20)
        worksheet.write("A1", "Username")
        worksheet.write("B1", "Password")
        i = 1

        user_list = []
        for number in range(data["number_from"], data["number_to"] + 1):
            raw_password = rand_str(data["password_length"])
            u = User(username=f"{data['prefix']}{number}{data['suffix']}",
                     password=make_password(raw_password))
            u.raw_password = raw_password
            user_list.append(u)

        try:
            with transaction.atomic():
                ret = User.objects.bulk_create(user_list)
                UserProfile.objects.bulk_create([UserProfile(user=u) for u in ret])
                for u in user_list:
                    worksheet.write_string(i, 0, u.username)
                    worksheet.write_string(i, 1, u.raw_password)
                    i += 1
                workbook.close()
                return self.success({"file_id": file_id})
        except IntegrityError as e:
            return self.error(str(e).split("\n")[1])


# ==== Group Management APIs ====

class GroupAPI(APIView):
    @super_admin_required
    def get(self, request):
        groups = Group.objects.all().order_by("name")
        return self.success(GroupSerializer(groups, many=True).data)

class GroupAssignAPI(APIView):
    @validate_serializer(AssignUsersToGroupSerializer)
    @super_admin_required
    def post(self, request):
        data = request.data
        name = data["group_name"].strip()
        group, _ = Group.objects.get_or_create(name=name)
        user_ids = data["user_ids"]

        if data.get("replace_existing"):
            UserGroup.objects.filter(user_id__in=user_ids).delete()

        existing = set(UserGroup.objects.filter(user_id__in=user_ids, group=group)
                       .values_list("user_id", flat=True))
        to_create = [UserGroup(user_id=uid, group=group) for uid in user_ids if uid not in existing]
        if to_create:
            UserGroup.objects.bulk_create(to_create)
        return self.success()

class GroupRemoveAPI(APIView):
    @super_admin_required
    def post(self, request):
        user_ids = request.data.get("user_ids") or []
        group_name = (request.data.get("group_name") or "").strip()
        if not user_ids or not group_name:
            return self.error("user_ids and group_name are required")
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return self.success()
        UserGroup.objects.filter(user_id__in=user_ids, group=group).delete()
        return self.success()

class GroupClearAPI(APIView):
    @validate_serializer(BulkUsersSerializer)
    @super_admin_required
    def post(self, request):
        user_ids = request.data["user_ids"]
        UserGroup.objects.filter(user_id__in=user_ids).delete()
        return self.success()
