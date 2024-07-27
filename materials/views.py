from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, serializers
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson, Subscription
from materials.pagination import MaterialsPagination
from materials.permissions import IsOwner, IsModerator
from materials.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from materials.services import create_stripe_price, create_stripe_session
from users.models import Payments
from users.serializers import PaymentSerializer

from .tasks import update_course_notification


# Create your views here.

class CourseViewSet(viewsets.ModelViewSet):
    pagination_class = MaterialsPagination
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    perms_methods = {
        'list': [IsAuthenticated, IsModerator | IsAdminUser],
        'retrieve': [IsAuthenticated, IsOwner | IsModerator | IsAdminUser],
        'create': [IsAuthenticated, ~IsModerator],
        'update': [IsAuthenticated, IsOwner | IsModerator],
        'partial_update': [IsAuthenticated, IsOwner | IsModerator],
        'destroy': [IsAuthenticated, IsOwner | IsAdminUser],
    }

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        course_id = course.id
        course.last_update = timezone.now()

        update_course_notification.delay(course_id)

    def get_permissions(self):
        self.permission_classes = self.perms_methods.get(self.action, self.permission_classes)
        return [permission() for permission in self.permission_classes]


class LessonListView(generics.ListAPIView):
    pagination_class = MaterialsPagination
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]


class LessonCreateView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LessonDeleteView(generics.DestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner, ~IsModerator]


class LessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerator | IsOwner | IsAdminUser]


class LessonUpdateView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsModerator | IsOwner]


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'method_payment']
    ordering_fields = ['payment_date']
    permission_classes = [IsModerator | IsOwner]


class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        course = serializer.validated_data.get('paid_course')
        if not course:
            raise serializers.ValidationError('Укажите курс')
        payment = serializer.save()
        stripe_price_id = create_stripe_price(payment)
        payment.payment_link, payment.payment_id = create_stripe_session(stripe_price_id)
        payment.save()


class PaymentDeleteView(generics.DestroyAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsOwner]


class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsModerator | IsOwner]


class PaymentUpdateView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsModerator | IsOwner]


class SubscribeAPIView(APIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):

        course = Course.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        subscription = Subscription.objects.filter(course=course, user=user).first()

        if subscription:

            if subscription.status:
                subscription.status = False
                subscription.save()
                message = 'Вы отписались от курса.'
            else:
                subscription.status = True
                subscription.save()
                message = 'Вы подписались на курс.'
        else:
            Subscription.objects.create(course=course, user=user, status=True)
            message = 'Вы подписались на курс.'

        return Response({"detail": message})