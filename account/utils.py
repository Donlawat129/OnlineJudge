# account/utils.py
from django.db.models import Q
from .models import Group

ADMIN_SET = ('Admin', 'Super Admin')

def is_admin_or_super(user) -> bool:
    return getattr(user, 'is_authenticated', False) and getattr(user, 'admin_type', '') in ADMIN_SET

def user_groups_qs(user):
    if not getattr(user, 'is_authenticated', False):
        return Group.objects.none()
    return Group.objects.filter(usergroup__user=user)

def filter_users_in_same_groups(qs, user):
    """
    กรอง queryset ของ User ให้เหลือเฉพาะคนที่ 'แชร์อย่างน้อยหนึ่งกลุ่ม' กับ user ปัจจุบัน
    - แอดมิน/ซุปเปอร์แอดมิน: เห็นทั้งหมด
    - ถ้า user ไม่อยู่ในกลุ่มไหนเลย: เห็นเฉพาะผู้ใช้ที่ 'ไม่มี' กลุ่ม (usergroup.isnull=True)
    """
    if is_admin_or_super(user):
        return qs
    ugs = user_groups_qs(user)
    if ugs.exists():
        return qs.filter(usergroup__group__in=ugs).distinct()
    else:
        return qs.filter(usergroup__isnull=True).distinct()
