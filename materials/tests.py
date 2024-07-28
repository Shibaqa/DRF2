from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        # Тестовый пользователь
        self.user = User(email='test@test.ru', phone='111111111', city='Testograd', is_superuser=False, is_staff=False,
                         is_active=True)
        self.user.set_password('123QWE456RTY')
        self.user.save()

        response = self.client.post(
            '/api/token/',
            {"email": "test@test.ru", "password": "123QWE456RTY"}
        )

        self.access_token = response.json().get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

        self.course = Course.objects.create(
            name="test_course",
        )

        # Создаем тестовый урок
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="This is a test lesson",
            user=self.user
        )

    def test_create_lesson(self):
        """
        Тест операции создания (create) проверки создания уроков
        """
        data = {
            "name": "test",
            "course": 1,
            "video": "https://www.youtube.com/",
            "description": "test description"
        }
        create_lesson = reverse('materials:lesson_create')
        response = self.client.post(create_lesson, data, format='json', **self.headers)
        print(response.json())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data['name'])

    def test_retrieve_lesson(self):
        """
        Тест операции чтения (retrieve) урока
        """
        retrieve_url = reverse('materials:lesson_detail', args=[self.lesson.id])
        response = self.client.get(retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.lesson.name)

    def test_update_lesson(self):
        # Тест операции обновления (update) урока
        update_url = reverse('materials:lesson_update', args=[self.lesson.id])
        updated_data = {
            "name": "Updated Lesson",
            "description": "This is an updated lesson",
        }
        response = self.client.patch(update_url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, updated_data['name'])
        self.assertEqual(self.lesson.description, updated_data['description'])

    def test_delete_lesson(self):
        # Тест операции удаления (delete) урока
        delete_url = reverse('materials:lesson_delete', args=[self.lesson.id])
        response = self.client.delete(delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_list_lessons(self):
        # Тест операции получения списка уроков
        list_url = reverse('materials:lesson_list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], self.lesson.name)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Тестовый пользователь
        self.user = User(email='test@test.ru', phone='111111111', city='Testograd', is_superuser=True, is_staff=True,
                         is_active=True)
        self.user.set_password('123QWE456RTY')
        self.user.save()

        response = self.client.post(
            '/api/token/',
            {"email": "test@test.ru", "password": "123QWE456RTY"}
        )

        self.access_token = response.json().get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

        # Тестовый курс
        self.course = Course.objects.create(
            name="test_course",
        )

        # Создаем тестовую подписку
        self.subscribe = Subscription.objects.create(
            user=self.user,
            course=self.course,
        )

    def test_subscribe_to_course(self):
        """
        Тест операции создания подписки на курс
        """
        subscribe_url = reverse('materials:subscribe', args=[self.course.id])
        response = self.client.post(subscribe_url, {}, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Вы подписались на курс.")

    def test_unsubscribe_from_course(self):
        """
        Тест операции отписки от курса
        """
        subscribe_url = reverse('materials:subscribe', args=[self.course.id])
        response = self.client.post(subscribe_url, {}, format='json', **self.headers)
        response = self.client.post(subscribe_url, {}, format='json', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Вы отписались от курса.")