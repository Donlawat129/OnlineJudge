from django import forms

from utils.api import serializers, UsernameSerializer

from .models import AdminType, ProblemPermission, User, UserProfile, UserGroup, Group


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32)
    password = serializers.CharField(min_length=6)
    email = serializers.EmailField(max_length=64)
    captcha = serializers.CharField()


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UserChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_email = serializers.EmailField(max_length=64)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class GenerateUserSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=16, allow_blank=True)
    suffix = serializers.CharField(max_length=16, allow_blank=True)
    number_from = serializers.IntegerField()
    number_to = serializers.IntegerField()
    password_length = serializers.IntegerField(max_value=16, default=8)


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(max_length=64))
    )


class UserAdminSerializer(serializers.ModelSerializer):
    real_name = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "admin_type", "problem_permission", "real_name",
            "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled",
            "groups"
        ]

    def get_real_name(self, obj):
        return obj.userprofile.real_name

    def get_groups(self, obj):
        return list(
            UserGroup.objects.filter(user=obj)
            .select_related("group")
            .values_list("group__name", flat=True)
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "admin_type", "problem_permission",
            "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    real_name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.show_real_name = kwargs.pop("show_real_name", False)
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_real_name(self, obj):
        return obj.real_name if self.show_real_name else None


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=32)
    real_name = serializers.CharField(max_length=32, allow_blank=True, allow_null=True)
    password = serializers.CharField(min_length=6, allow_blank=True, required=False, default=None)
    email = serializers.EmailField(max_length=64)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class EditUserProfileSerializer(serializers.Serializer):
    real_name = serializers.CharField(max_length=32, allow_null=True, required=False)
    avatar = serializers.CharField(max_length=256, allow_blank=True, required=False)
    blog = serializers.URLField(max_length=256, allow_blank=True, required=False)
    mood = serializers.CharField(max_length=256, allow_blank=True, required=False)
    github = serializers.URLField(max_length=256, allow_blank=True, required=False)
    school = serializers.CharField(max_length=64, allow_blank=True, required=False)
    major = serializers.CharField(max_length=64, allow_blank=True, required=False)
    language = serializers.CharField(max_length=32, allow_blank=True, required=False)


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6)
    captcha = serializers.CharField()


class SSOSerializer(serializers.Serializer):
    token = serializers.CharField()


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class FileUploadForm(forms.Form):
    file = forms.FileField()


class RankInfoSerializer(serializers.ModelSerializer):
    user = UsernameSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"


# ===== Group serializers =====
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class GroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)


class AssignUsersToGroupSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False
    )
    group_name = serializers.CharField(max_length=64, allow_blank=False)
    replace_existing = serializers.BooleanField(required=False, default=False)

    def validate_group_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Group name cannot be blank.")
        return value

    def validate_user_ids(self, value):
        ids = list(dict.fromkeys(value))  # unique + keep order
        if not ids:
            raise serializers.ValidationError("At least one user id is required.")
        existed = set(User.objects.filter(id__in=ids).values_list("id", flat=True))
        missing = [i for i in ids if i not in existed]
        if missing:
            raise serializers.ValidationError(f"User id(s) not found: {missing}")
        return ids
