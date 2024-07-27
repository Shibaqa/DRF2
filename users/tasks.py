from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def check_user_activity(user_id):
    user = User.objects.get(id=user_id)
    if user.last_login < timezone.now() - timezone.timedelta(days=30):
        user.is_active = False
        user.save()