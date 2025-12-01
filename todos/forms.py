from django import forms
from .models import Todo

class TodoForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )

    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter todo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
