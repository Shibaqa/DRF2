from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from materials.models import Course, Lesson

# Create your models here.

NULLABLE = {'null': True, 'blank': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, max_length=254, verbose_name='email')

    avatar = models.ImageField(upload_to='users/', verbose_name='avatar', **NULLABLE)
    phone = models.CharField(max_length=20, verbose_name='phone', **NULLABLE)
    city = models.CharField(max_length=50, verbose_name='city', **NULLABLE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class Payments(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'
    PAYMENT_CHOICES = [
        (CASH, 'наличные'),
        (TRANSFER, 'перевод')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, **NULLABLE, on_delete=models.CASCADE,
                             verbose_name='пользователь')
    payment_date = models.DateField(auto_now_add=True, verbose_name='дата платежа')
    paid_course = models.ForeignKey(Course, on_delete=models.CASCADE, **NULLABLE, verbose_name='оплаченный курс')
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, **NULLABLE, verbose_name='оплаченный урок')
    payment_amount = models.PositiveIntegerField(verbose_name='сумма оплаты')
    method_payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default=CASH,
                                      verbose_name='способ оплаты')
    payment_link = models.URLField(max_length=400, **NULLABLE, verbose_name='ссылка на оплату')
    payment_id = models.CharField(max_length=100, **NULLABLE, verbose_name='идентификатор платежа')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'

    def __str__(self):
        return f'{self.user}: ({self.paid_course if self.paid_course else self.paid_lesson})'