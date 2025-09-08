# account/utils.py
from django.db.models import Q
from .models import Group, UserGroup

ADMIN_SET = ('Admin', 'Super Admin')

def is_admin_or_super(user) -> bool:
    return getattr(user, 'is_authenticated', False) and getattr(user, 'admin_type', '') in ADMIN_SET

def user_groups_qs(user):
    """คืน QuerySet ของกลุ่มที่ user สังกัด; ถ้าไม่ล็อกอิน คืน empty QS"""
    if not getattr(user, 'is_authenticated', False):
        return Group.objects.none()
    return Group.objects.filter(usergroup__user=user)

def filter_by_user_groups(qs, user, *, visible_field='visible', m2m_field='groups'):
    """
    ฟิลเตอร์ queryset ตามสิทธิ์กลุ่ม:
      - แอดมินเห็นทั้งหมด
      - ผู้ใช้ทั่วไป: ต้องเป็น visible และ (ไม่ผูกกลุ่ม) หรือ (อยู่ในกลุ่ม)
    ใช้ได้กับโมเดลที่มีฟิลด์ visible และ M2M ชื่อ groups (เช่น Problem)
    """
    if is_admin_or_super(user):
        return qs
    groups = user_groups_qs(user)
    return qs.filter(**{visible_field: True}).filter(
        Q(**{f'{m2m_field}__isnull': True}) | Q(**{f'{m2m_field}__in': groups})
    ).distinct()
