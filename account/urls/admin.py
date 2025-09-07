# account/urls/admin.py
from django.conf.urls import url
from ..views.admin import (
    UserAdminAPI, GenerateUserAPI,
    GroupAPI, GroupAssignAPI, GroupRemoveAPI, GroupClearAPI
)

urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),

    url(r"^groups/?$", GroupAPI.as_view(), name="group_list_api"),
    url(r"^groups/assign/?$", GroupAssignAPI.as_view(), name="group_assign_api"),
    url(r"^groups/remove/?$", GroupRemoveAPI.as_view(), name="group_remove_api"),
    url(r"^groups/clear/?$", GroupClearAPI.as_view(), name="group_clear_api"),
]
