from typing import Dict, List, Optional

from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


GROUPS = {
    "gate_managers": {
        "ticket model": ["view"],
    },
    "check_in_managers": {
        "flight model": ["view", "add", "change", "delete"],
    },
    "supervisors": {
        "ticket model": ["view"],
        "flight model": ["view", "add", "change", "delete"],
        "user": ["view", "add", "change", "delete"],
    },
}


def get_permission_by_name(name: str) -> Optional[Permission]:
    """Gets the permission with the given name.

    Args:
        name: The name of the permission to get.

    Returns:
        The permission with the given name, or None if the permission does not exist.
    """
    return Permission.objects.get(name=name)


def assign_permissions_from_dict(group: Group, permissions_dict: Dict[str, List[str]]) -> None:
    """Assigns the permissions from the given dictionary to the group.

    Args:
        group: The group to assign the permissions to.
        permissions_dict: The dictionary of permissions to assign to the group.
    """
    for model, permissions in permissions_dict.items():
        for permission in permissions:
            permission_name = f"Can {permission} {model}"
            model_add_perm = get_permission_by_name(permission_name)
            if model_add_perm is not None:
                group.permissions.add(model_add_perm)


class Command(BaseCommand):
    help = "Creates staff groups"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        for group, models in GROUPS.items():
            new_group, created = Group.objects.get_or_create(name=group)
            assign_permissions_from_dict(new_group, models)
