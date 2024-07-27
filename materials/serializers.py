from rest_framework import serializers

from materials.models import Lesson, Course, Subscription
from materials.validators import VideoValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        validators = [VideoValidator(field='video')]
        fields = (
            "name",
            "description",
            "preview",
            "video",
            "user",
        )


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, source="lesson_set", read_only=True)
    lessons_count = serializers.SerializerMethodField()
    subscription = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        return Lesson.objects.filter(course=obj).count()

    def get_subscription(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user = request.user
            course = obj
            subscription = Subscription.objects.filter(course=course, user=user).first()
            if subscription:
                return subscription.status
        return False

    class Meta:
        model = Course
        fields = (
            "name",
            "preview",
            "description",
            "user",
            "lessons_count",
            "lessons",
            "subscription",
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'