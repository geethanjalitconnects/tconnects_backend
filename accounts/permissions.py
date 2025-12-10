from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    """
    Allows access only to users with role 'recruiter'.
    """

    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and getattr(request.user, "role", None) == "recruiter"
        )
