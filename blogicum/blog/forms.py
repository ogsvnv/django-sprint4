from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import Comment, Post, User


class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'first_name',
            'last_name',
            'email',
        )


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(
            pk=self.instance.pk
        ).exists():
            raise ValidationError('Этот email уже используется')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(
            pk=self.instance.pk
        ).exists():
            raise ValidationError('Это имя пользователя уже занято')
        return username


class PostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author', 'created_at')
        widgets = {
            'text': forms.Textarea({'rows': '5'}),
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'image': forms.ClearableFileInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].required = True
        self.fields['is_published'].initial = True
        self.fields['location'].required = False
        self.fields['image'].required = False

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise ValidationError('Категория обязательна для заполнения')
        return category


class CommentEditForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea({'rows': '3'})
        }
