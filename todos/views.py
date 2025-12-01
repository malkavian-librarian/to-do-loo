from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Todo
from .forms import TodoForm

class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10

class TodoDetailView(DetailView):
    model = Todo
    template_name = 'todos/todo_detail.html'
    context_object_name = 'todo'

class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo-list')

class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo-list')

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todo-list')

def toggle_todo(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    return redirect('todo-list')
