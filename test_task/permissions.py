from rest_framework import permissions
from test_task.models import Box

# permission to check if user has staff access or not
class IsStaffPermission(permissions.BasePermission):
    """
    Permission check for staff user.
    """

    def has_permission(self, request, view):
        return request.user.is_staff


# permission to check if user is staff access or requesting user is requesting for his data only
class IsStaffAndSelf(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff and obj.user == request.user