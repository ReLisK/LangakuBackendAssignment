from rest_framework import permissions, status
from assignment.models import IdempotencyKeys
from django.utils import timezone
from datetime import timedelta

Ikey_TTL = 24


class IdempotencyPermission(permissions.BasePermission):
    """
    This checks if an API call is idempotent, if not it denies the call.
    """

    message = "Duplicate request denied"

    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        ikey = request.META.get("HTTP_X_IDEMPOTENCY_KEY")
        if not ikey or ikey is None:
            self.message = "No X_IDEMPOTENCY_KEY provided"
            return False
        currentDateTime = timezone.now()
        try:
            # Will need to cleanup expired keys from db
            IdempotencyKeys.objects.get(pk=ikey, expires_at__gte=currentDateTime)
            return False
        except IdempotencyKeys.DoesNotExist:
            expiryDate = currentDateTime + timedelta(hours=Ikey_TTL)

            IdempotencyKeys.objects.create(
                key=ikey, status_code=status.HTTP_200_OK, expires_at=expiryDate
            )
            return True
