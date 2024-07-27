from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    message = 'Вы не являетесь модератором!'

    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderator').exists()

    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderator').exists():
            return True
        return False


class IsOwner(permissions.BasePermission):
    message = 'Вы не являетесь владельцем!'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user