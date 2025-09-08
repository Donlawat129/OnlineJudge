# account/utils.py
from .models import UserGroup

ADMIN_SET = ('Admin', 'Super Admin')

def is_admin_or_super(user) -> bool:
    return getattr(user, 'is_authenticated', False) and getattr(user, 'admin_type', '') in ADMIN_SET

def filter_users_in_same_groups(qs, user):
    """
    แอดมิน/ซุปเปอร์แอดมิน: เห็นทั้งหมด
    ผู้ใช้ทั่วไป: เห็นเฉพาะผู้ใช้ที่แชร์อย่างน้อยหนึ่งกลุ่มกับตน
    ถ้าไม่ได้อยู่ในกลุ่มใดเลย: เห็นเฉพาะคนที่ไม่มีกลุ่ม
    """
    if not getattr(user, 'is_authenticated', False):
        # ผู้ไม่ได้ล็อกอิน ก็ไม่เห็นใคร (หรือจะคืน qs.none() ก็ได้)
        return qs.none()

    if is_admin_or_super(user):
        return qs

    # กลุ่มของ user ปัจจุบัน
    g_ids = list(UserGroup.objects.filter(user=user).values_list('group_id', flat=True))
    if g_ids:
        # user id ทั้งหมดที่อยู่ในกลุ่มเหล่านี้
        u_ids = UserGroup.objects.filter(group_id__in=g_ids).values_list('user_id', flat=True)
        return qs.filter(id__in=u_ids).distinct()
    else:
        # ไม่มีสังกัด -> เห็นเฉพาะผู้ใช้ที่ก็ไม่มีสังกัดเช่นกัน
        grouped_user_ids = UserGroup.objects.values_list('user_id', flat=True).distinct()
        return qs.exclude(id__in=grouped_user_ids)
