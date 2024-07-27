from django.urls import path
from rest_framework.routers import DefaultRouter

from materials.apps import CourseAppConfig
from materials.views import CourseViewSet, LessonListView, LessonCreateView, LessonDetailView, LessonUpdateView, \
    LessonDeleteView, PaymentListView, PaymentCreateView, PaymentDetailView, PaymentUpdateView, PaymentDeleteView, \
    SubscribeAPIView

app_name = CourseAppConfig.name

router = DefaultRouter()
router.register(r'course', CourseViewSet, basename='course')

urlpatterns = [
    path('lesson/', LessonListView.as_view(), name='lesson_list'),
    path('lesson/create/', LessonCreateView.as_view(), name='lesson_create'),
    path('lesson/detail/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('lesson/update/<int:pk>/', LessonUpdateView.as_view(), name='lesson_update'),
    path('lesson/delete/<int:pk>/', LessonDeleteView.as_view(), name='lesson_delete'),

    path('payment/', PaymentListView.as_view(), name='payment_list'),
    path('payment/create/', PaymentCreateView.as_view(), name='payment_create'),
    path('paymentv/detail/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('payment/update/<int:pk>/', PaymentUpdateView.as_view(), name='payment_update'),
    path('payment/delete/<int:pk>/', PaymentDeleteView.as_view(), name='payment_delete'),

    path('course/<int:pk>/subscription/', SubscribeAPIView.as_view(), name='subscribe'),
] + router.urls