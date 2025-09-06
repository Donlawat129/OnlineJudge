from django.conf.urls import url

from ..views.admin import UserAdminAPI, GenerateUserAPI
# [ADD]
from ..views.group import (
    GroupAdminAPI, AssignUsersToGroupAPI,
    RemoveUsersFromGroupAPI, ClearUsersGroupsAPI
)

urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),

    # [ADD] group endpoints
    url(r"^groups/?$", GroupAdminAPI.as_view(), name="group_admin_api"),
    url(r"^groups/assign/?$", AssignUsersToGroupAPI.as_view(), name="group_assign_api"),
    url(r"^groups/remove/?$", RemoveUsersFromGroupAPI.as_view(), name="group_remove_api"),
    url(r"^groups/clear/?$", ClearUsersGroupsAPI.as_view(), name="group_clear_api"),
]
