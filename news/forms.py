from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Article, Newsletter, Publisher


class RegistrationForm(UserCreationForm):
    """Form for user registration with role selection."""
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        """Saves the user and assigns role-based permissions."""
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
            user.assign_group_and_permissions()  # Ensure this runs after save
        return user


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']  # Journalist sets via view


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name']


class SubscriptionForm(forms.Form):
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(), required=False
    )
    journalists = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='journalist'), required=False
    )
