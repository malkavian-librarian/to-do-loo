from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo


class TodoModelTests(TestCase):
    """Test cases for the Todo model."""

    def setUp(self):
        """Create a test todo."""
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="This is a test todo",
            due_date=timezone.now() + timedelta(days=1),
            completed=False
        )

    def test_todo_creation(self):
        """Test that a todo is created with correct attributes."""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "This is a test todo")
        self.assertFalse(self.todo.completed)
        self.assertIsNotNone(self.todo.created_at)
        self.assertIsNotNone(self.todo.updated_at)

    def test_todo_string_representation(self):
        """Test the string representation of a todo."""
        self.assertEqual(str(self.todo), "Test Todo")

    def test_todo_default_not_completed(self):
        """Test that newly created todos are not completed by default."""
        new_todo = Todo.objects.create(title="New Todo")
        self.assertFalse(new_todo.completed)

    def test_todo_can_be_marked_complete(self):
        """Test that a todo can be marked as completed."""
        self.todo.completed = True
        self.todo.save()
        refreshed_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertTrue(refreshed_todo.completed)

    def test_todo_description_is_optional(self):
        """Test that todo description is optional."""
        todo_without_description = Todo.objects.create(
            title="No Description Todo"
        )
        self.assertEqual(todo_without_description.description, "")

    def test_todo_due_date_is_optional(self):
        """Test that todo due_date is optional."""
        todo_without_due_date = Todo.objects.create(
            title="No Due Date Todo"
        )
        self.assertIsNone(todo_without_due_date.due_date)


class TodoViewTests(TestCase):
    """Test cases for Todo views."""

    def setUp(self):
        """Set up test client and create test todos."""
        self.client = Client()
        self.todo1 = Todo.objects.create(
            title="Buy groceries",
            description="Milk, eggs, bread",
            due_date=timezone.now() + timedelta(days=1),
            completed=False
        )
        self.todo2 = Todo.objects.create(
            title="Complete project",
            description="Finish the Django project",
            completed=True
        )

    def test_todo_list_view(self):
        """Test that the todo list view displays all todos."""
        response = self.client.get(reverse('todo-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buy groceries")
        self.assertContains(response, "Complete project")
        self.assertEqual(len(response.context['todos']), 2)

    def test_todo_list_view_template(self):
        """Test that the correct template is used for todo list."""
        response = self.client.get(reverse('todo-list'))
        self.assertTemplateUsed(response, 'todos/todo_list.html')

    def test_todo_detail_view(self):
        """Test that the todo detail view displays a single todo."""
        response = self.client.get(reverse('todo-detail', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buy groceries")
        self.assertContains(response, "Milk, eggs, bread")
        self.assertEqual(response.context['todo'], self.todo1)

    def test_todo_detail_view_template(self):
        """Test that the correct template is used for todo detail."""
        response = self.client.get(reverse('todo-detail', args=[self.todo1.pk]))
        self.assertTemplateUsed(response, 'todos/todo_detail.html')

    def test_todo_detail_view_not_found(self):
        """Test that detail view returns 404 for non-existent todo."""
        response = self.client.get(reverse('todo-detail', args=[999]))
        self.assertEqual(response.status_code, 404)


class TodoCreateViewTests(TestCase):
    """Test cases for creating todos."""

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    def test_todo_create_view_get(self):
        """Test that the create view displays the form."""
        response = self.client.get(reverse('todo-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
        self.assertIn('form', response.context)

    def test_todo_create_view_post_success(self):
        """Test that a todo can be created via POST."""
        data = {
            'title': 'New Todo',
            'description': 'This is a new todo',
            'completed': False
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Todo.objects.filter(title='New Todo').exists())
        self.assertEqual(Todo.objects.get(title='New Todo').description, 'This is a new todo')

    def test_todo_create_view_post_redirect(self):
        """Test that creating a todo redirects to the list view."""
        data = {
            'title': 'Another Todo',
            'description': 'Description',
            'completed': False
        }
        response = self.client.post(reverse('todo-create'), data, follow=True)
        self.assertRedirects(response, reverse('todo-list'))

    def test_todo_create_with_due_date(self):
        """Test that a todo can be created with a due date."""
        due_date = timezone.now() + timedelta(days=5)
        data = {
            'title': 'Todo with due date',
            'description': 'Has a due date',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M'),
            'completed': False
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 302)
        todo = Todo.objects.get(title='Todo with due date')
        self.assertIsNotNone(todo.due_date)

    def test_todo_create_title_required(self):
        """Test that title is required when creating a todo."""
        data = {
            'title': '',
            'description': 'No title',
            'completed': False
        }
        response = self.client.post(reverse('todo-create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Todo.objects.filter(description='No title').exists())


class TodoUpdateViewTests(TestCase):
    """Test cases for updating todos."""

    def setUp(self):
        """Set up test client and create a test todo."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Original Title",
            description="Original Description",
            completed=False
        )

    def test_todo_edit_view_get(self):
        """Test that the edit view displays the form with existing data."""
        response = self.client.get(reverse('todo-edit', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_form.html')
        self.assertContains(response, "Original Title")

    def test_todo_update_title(self):
        """Test that a todo's title can be updated."""
        data = {
            'title': 'Updated Title',
            'description': 'Original Description',
            'completed': False
        }
        response = self.client.post(reverse('todo-edit', args=[self.todo.pk]), data)
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertEqual(updated_todo.title, 'Updated Title')

    def test_todo_update_description(self):
        """Test that a todo's description can be updated."""
        data = {
            'title': 'Original Title',
            'description': 'Updated Description',
            'completed': False
        }
        response = self.client.post(reverse('todo-edit', args=[self.todo.pk]), data)
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertEqual(updated_todo.description, 'Updated Description')

    def test_todo_update_title_and_description(self):
        """Test that both title and description can be updated together."""
        data = {
            'title': 'New Title',
            'description': 'New Description',
            'completed': False
        }
        response = self.client.post(reverse('todo-edit', args=[self.todo.pk]), data)
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertEqual(updated_todo.title, 'New Title')
        self.assertEqual(updated_todo.description, 'New Description')

    def test_todo_update_completed_status(self):
        """Test that a todo's completed status can be toggled."""
        data = {
            'title': 'Original Title',
            'description': 'Original Description',
            'completed': True
        }
        response = self.client.post(reverse('todo-edit', args=[self.todo.pk]), data)
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo.pk)
        self.assertTrue(updated_todo.completed)

    def test_todo_update_redirect(self):
        """Test that updating a todo redirects to the list view."""
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': False
        }
        response = self.client.post(
            reverse('todo-edit', args=[self.todo.pk]), data, follow=True
        )
        self.assertRedirects(response, reverse('todo-list'))


class TodoDeleteViewTests(TestCase):
    """Test cases for deleting todos."""

    def setUp(self):
        """Set up test client and create a test todo."""
        self.client = Client()
        self.todo = Todo.objects.create(
            title="Todo to Delete",
            description="This will be deleted",
            completed=False
        )

    def test_todo_delete_view_get(self):
        """Test that the delete confirmation page is displayed."""
        response = self.client.get(reverse('todo-delete', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todos/todo_confirm_delete.html')
        self.assertContains(response, "Todo to Delete")

    def test_todo_delete_view_post(self):
        """Test that a todo can be deleted via POST."""
        todo_id = self.todo.pk
        response = self.client.post(reverse('todo-delete', args=[todo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=todo_id).exists())

    def test_todo_delete_redirect(self):
        """Test that deleting a todo redirects to the list view."""
        response = self.client.post(
            reverse('todo-delete', args=[self.todo.pk]), follow=True
        )
        self.assertRedirects(response, reverse('todo-list'))

    def test_todo_delete_not_found(self):
        """Test that deleting a non-existent todo returns 404."""
        response = self.client.get(reverse('todo-delete', args=[999]))
        self.assertEqual(response.status_code, 404)


class TodoToggleViewTests(TestCase):
    """Test cases for toggling todo completion status."""

    def setUp(self):
        """Set up test client and create test todos."""
        self.client = Client()
        self.todo_pending = Todo.objects.create(
            title="Pending Todo",
            completed=False
        )
        self.todo_completed = Todo.objects.create(
            title="Completed Todo",
            completed=True
        )

    def test_toggle_pending_to_completed(self):
        """Test that toggling a pending todo marks it as completed."""
        response = self.client.post(reverse('todo-toggle', args=[self.todo_pending.pk]))
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo_pending.pk)
        self.assertTrue(updated_todo.completed)

    def test_toggle_completed_to_pending(self):
        """Test that toggling a completed todo marks it as pending."""
        response = self.client.post(reverse('todo-toggle', args=[self.todo_completed.pk]))
        self.assertEqual(response.status_code, 302)
        updated_todo = Todo.objects.get(pk=self.todo_completed.pk)
        self.assertFalse(updated_todo.completed)

    def test_toggle_redirect(self):
        """Test that toggling a todo redirects to the list view."""
        response = self.client.post(
            reverse('todo-toggle', args=[self.todo_pending.pk]), follow=True
        )
        self.assertRedirects(response, reverse('todo-list'))

    def test_toggle_not_found(self):
        """Test that toggling a non-existent todo returns 404."""
        response = self.client.post(reverse('todo-toggle', args=[999]))
        self.assertEqual(response.status_code, 404)
