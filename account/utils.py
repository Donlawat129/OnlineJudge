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

def filter_by_user_groups(qs, user, *, visible_field='visible', m2m_field='groups'):
    if is_admin_or_super(user):
        return qs
    ugs = user_groups_qs(user)
    return qs.filter(**{visible_field: True}).filter(
        Q(**{f'{m2m_field}__isnull': True}) | Q(**{f'{m2m_field}__in': ugs})
    ).distinct()
