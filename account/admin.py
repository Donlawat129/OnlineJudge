from django.contrib import admin
from .models import Group, UserGroup

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_by", "created_at")
    search_fields = ("name",)

@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "group", "joined_at")
    search_fields = ("user__username", "group__name")
