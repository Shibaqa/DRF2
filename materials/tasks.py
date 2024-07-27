from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from materials.models import Subscription


@shared_task
def update_course_notification(course_id):
    subscriptions = Subscription.objects.filter(course_id=course_id, status=True)

    for sub in subscriptions:
        if sub.course.last_update < timezone.now() + timezone.timedelta(hours=4):
            send_mail(
                subject='Обновление курса',
                message=f'Курс {sub.course.name} был обновлен.',
                from_email=EMAIL_HOST_USER,
                recipient_list=[sub.user.email],
            )
