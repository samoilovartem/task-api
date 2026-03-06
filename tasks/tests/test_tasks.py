from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from tasks.models import Task

User = get_user_model()


class TaskAPITestCase(TestCase):
    """Test suite for task CRUD operations and access control."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        response = self.client.post('/api/tasks/', {'title': 'Test task', 'description': 'desc'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.first()
        self.assertEqual(task.title, 'Test task')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.status)

    def test_create_task_without_description(self):
        response = self.client.post('/api/tasks/', {'title': 'No desc'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['description'], '')

    def test_create_task_without_title_fails(self):
        response = self.client.post('/api/tasks/', {'description': 'no title'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_task_with_blank_title_fails(self):
        response = self.client.post('/api/tasks/', {'title': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_task_default_status_false(self):
        response = self.client.post('/api/tasks/', {'title': 'Task'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['status'])

    def test_create_task_with_status_true(self):
        response = self.client.post('/api/tasks/', {'title': 'Done task', 'status': True})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['status'])

    def test_list_tasks(self):
        Task.objects.create(title='Task 1', user=self.user)
        Task.objects.create(title='Task 2', user=self.user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_tasks_excludes_other_users(self):
        Task.objects.create(title='My task', user=self.user)
        Task.objects.create(title='Their task', user=self.other_user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'My task')

    def test_list_tasks_empty(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_task(self):
        task = Task.objects.create(title='Detail', description='details', user=self.user)
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Detail')
        self.assertEqual(response.data['description'], 'details')
        self.assertIn('id', response.data)
        self.assertIn('created_at', response.data)

    def test_retrieve_nonexistent_task(self):
        response = self.client.get('/api/tasks/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_access_other_users_task(self):
        task = Task.objects.create(title='Other task', user=self.other_user)
        response = self.client.get(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        task = Task.objects.create(title='Old', description='old desc', user=self.user)
        response = self.client.put(
            f'/api/tasks/{task.id}/',
            {
                'title': 'New',
                'description': 'new desc',
                'status': True,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'New')
        self.assertEqual(task.description, 'new desc')
        self.assertTrue(task.status)

    def test_partial_update_task(self):
        task = Task.objects.create(title='Original', description='keep', user=self.user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {'title': 'Changed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Changed')
        self.assertEqual(task.description, 'keep')

    def test_mark_task_complete(self):
        task = Task.objects.create(title='Todo', user=self.user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {'status': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.status)

    def test_cannot_update_other_users_task(self):
        task = Task.objects.create(title='Not mine', user=self.other_user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Not mine')

    def test_delete_task(self):
        task = Task.objects.create(title='Delete me', user=self.user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_cannot_delete_other_users_task(self):
        task = Task.objects.create(title='Not mine', user=self.other_user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.count(), 1)

    def test_filter_tasks_by_status(self):
        Task.objects.create(title='Done', status=True, user=self.user)
        Task.objects.create(title='Not done', status=False, user=self.user)
        response = self.client.get('/api/tasks/', {'status': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Done')

    def test_filter_tasks_by_status_false(self):
        Task.objects.create(title='Done', status=True, user=self.user)
        Task.objects.create(title='Not done', status=False, user=self.user)
        response = self.client.get('/api/tasks/', {'status': 'false'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Not done')

    def test_created_at_is_read_only(self):
        response = self.client.post(
            '/api/tasks/',
            {
                'title': 'Task',
                'created_at': '2000-01-01T00:00:00Z',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['created_at'][:4], '2000')

    def test_id_is_read_only(self):
        response = self.client.post('/api/tasks/', {'title': 'Task', 'id': 99999})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 99999)

    def test_list_tasks_ordered_by_newest_first(self):
        t1 = Task.objects.create(title='First', user=self.user)
        t2 = Task.objects.create(title='Second', user=self.user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.data[0]['id'], t2.id)
        self.assertEqual(response.data[1]['id'], t1.id)


class TaskUnauthenticatedTestCase(TestCase):
    """Test suite for unauthenticated access to task endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_list_tasks_unauthenticated(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_unauthenticated(self):
        response = self.client.post('/api/tasks/', {'title': 'Nope'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_task_unauthenticated(self):
        user = User.objects.create_user(username='u', password='testpass123')
        task = Task.objects.create(title='Task', user=user)
        response = self.client.patch(f'/api/tasks/{task.id}/', {'title': 'Hacked'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_task_unauthenticated(self):
        user = User.objects.create_user(username='u', password='testpass123')
        task = Task.objects.create(title='Task', user=user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RegisterAPITestCase(TestCase):
    """Test suite for user registration endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'newuser',
                'password': 'securepass123',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_duplicate_username(self):
        User.objects.create_user(username='taken', password='testpass123')
        response = self.client.post(
            '/api/register/',
            {
                'username': 'taken',
                'password': 'securepass123',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_short_password(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'newuser',
                'password': 'short',
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_missing_password(self):
        response = self.client.post('/api/register/', {'username': 'newuser'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_username(self):
        response = self.client.post('/api/register/', {'password': 'securepass123'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registered_user_password_is_hashed(self):
        self.client.post(
            '/api/register/',
            {
                'username': 'hashcheck',
                'password': 'securepass123',
            },
        )
        user = User.objects.get(username='hashcheck')
        self.assertTrue(user.check_password('securepass123'))
        self.assertNotEqual(user.password, 'securepass123')


class TaskModelTestCase(TestCase):
    """Test suite for Task model behavior."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_str_representation(self):
        task = Task.objects.create(title='My Task', user=self.user)
        self.assertEqual(str(task), 'My Task')

    def test_default_ordering(self):
        t1 = Task.objects.create(title='First', user=self.user)
        t2 = Task.objects.create(title='Second', user=self.user)
        tasks = list(Task.objects.filter(user=self.user))
        self.assertEqual(tasks[0].id, t2.id)
        self.assertEqual(tasks[1].id, t1.id)

    def test_cascade_delete_user(self):
        Task.objects.create(title='Task', user=self.user)
        self.user.delete()
        self.assertEqual(Task.objects.count(), 0)
