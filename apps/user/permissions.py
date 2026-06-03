from rest_framework.permissions import BasePermission

class IsAdminOrReadOnlyOutputsSeller(BasePermission):
    """
    Admin: acceso total
    Vendedor: solo a outputs
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin total
        if user.is_superuser or user.is_admin:
            return True

        # Vendedor
        is_seller = user.is_staff and not user.is_admin and not user.is_superuser
        if not is_seller:
            return False

        # Solo permitir outputs
        allowed_basenames = {"orders", "order", "outputs", "output"}
        current_basename = getattr(view, "basename", None)

        return current_basename in allowed_basenames