from rest_framework import permissions


class IsModeratorOrCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        else:
            return request.user.is_moderator is True
