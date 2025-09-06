from django.conf.urls import url

from ..views.admin import UserAdminAPI, GenerateUserAPI
# [ADD]
from ..views.admin import AdminGroupAPI, AdminAssignUsersToGroupAPI

urlpatterns = [
    url(r"^user/?$", UserAdminAPI.as_view(), name="user_admin_api"),
    url(r"^generate_user/?$", GenerateUserAPI.as_view(), name="generate_user_api"),
]

# [ADD]
urlpatterns += [
    url(r"^groups/?$", AdminGroupAPI.as_view(), name="admin_group_api"),
    url(r"^groups/assign/?$", AdminAssignUsersToGroupAPI.as_view(), name="admin_group_assign_api"),
]
