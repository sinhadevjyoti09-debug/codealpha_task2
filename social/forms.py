from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Profile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-input',
                'autocomplete': 'off',
            })
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': "What's on your mind?",
                'rows': 3,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'accept': 'video/*',
            }),
        }
        labels = {
            'content': '',
            'image': '📷 Add Photo',
            'video': '🎬 Add Video',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Write a comment...',
            })
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
            'bio': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tell us about yourself...',
            }),
        }
        labels = {
            'avatar': '📷 Profile Picture',
            'bio': 'Bio',
        }
