from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.mail import send_mass_mail
from .twitter_api import tweet_new_article, tweet_new_newsletter


class CustomUser(AbstractUser):
    """Custom user model with roles and subscriptions."""
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('journalist', 'Journalist'),
    )
    role = models.CharField(max_length=20,
                            choices=ROLE_CHOICES,
                            default='reader')
    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='subscribers')
    subscribed_journalists = models.ManyToManyField(
        'self', blank=True, symmetrical=False,
        related_name='subscribers_journalists')
    independent_articles = models.ManyToManyField(
        'Article', blank=True,
        related_name='independent_journalist_articles')
    independent_newsletters = models.ManyToManyField(
        'Newsletter', blank=True,
        related_name='independent_journalist_newsletters')

    def __str__(self):
        return self.username

    def assign_group_and_permissions(self):
        """Assigns group and permissions based on user role."""
        if self.role not in dict(self.ROLE_CHOICES):
            raise ValueError("Invalid role")
        group_name = self.role.capitalize() + 's'
        group, _ = Group.objects.get_or_create(name=group_name)
        self.groups.add(group)
        ct_article = ContentType.objects.get_for_model(Article)
        ct_newsletter = ContentType.objects.get_for_model(Newsletter)

        if self.role == 'reader':
            group.permissions.add(
                Permission.objects.get(
                    content_type=ct_article,
                    codename='view_article'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='view_newsletter')
            )
        elif self.role == 'editor':
            group.permissions.add(
                Permission.objects.get(
                    content_type=ct_article,
                    codename='view_article'),
                Permission.objects.get(
                    content_type=ct_article,
                    codename='change_article'),
                Permission.objects.get(
                    content_type=ct_article,
                    codename='delete_article'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='view_newsletter'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='change_newsletter'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='delete_newsletter')
            )
        elif self.role == 'journalist':
            group.permissions.add(
                Permission.objects.get(
                    content_type=ct_article,
                    codename='add_article'),
                Permission.objects.get(
                    content_type=ct_article,
                    codename='view_article'),
                Permission.objects.get(
                    content_type=ct_article,
                    codename='change_article'),
                Permission.objects.get(
                    content_type=ct_article,
                    codename='delete_article'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='add_newsletter'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='view_newsletter'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='change_newsletter'),
                Permission.objects.get(
                    content_type=ct_newsletter,
                    codename='delete_newsletter')
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.assign_group_and_permissions()
        if self.role != 'reader':
            self.subscribed_publishers.clear()
            self.subscribed_journalists.clear()


class Publisher(models.Model):
    name = models.CharField(max_length=255)
    editors = models.ManyToManyField(
        CustomUser,
        related_name='edited_publishers',
        limit_choices_to={'role': 'editor'})
    journalists = models.ManyToManyField(
        CustomUser,
        related_name='journalist_publishers',
        limit_choices_to={'role': 'journalist'})

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True, blank=True)
    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True, blank=True,
        limit_choices_to={'role': 'journalist'})
    approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def approve(self):
        self.approved = True
        self.save()
        subscribers = set()
        if self.publisher:
            subscribers.update(
                self.publisher.subscribers.all())
        if self.journalist:
            subscribers.update(
                self.journalist.subscribers_journalists.all())
        messages = [
            ('New Article: ' + self.title, self.content,
             settings.DEFAULT_FROM_EMAIL, [sub.email])
            for sub in subscribers if sub.email
        ]
        send_mass_mail(messages, fail_silently=True)
        tweet_new_article(self)


class Newsletter(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True, blank=True)
    journalist = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE, null=True,
        blank=True,
        limit_choices_to={'role': 'journalist'})
    approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def approve(self):
        self.approved = True
        self.save()
        subscribers = set()
        if self.publisher:
            subscribers.update(
                self.publisher.subscribers.all())
        if self.journalist:
            subscribers.update(
                self.journalist.subscribers_journalists.all())
        messages = [
            ('New Newsletter: ' + self.title,
             self.content, settings.DEFAULT_FROM_EMAIL, [sub.email])
            for sub in subscribers if sub.email]
        send_mass_mail(messages, fail_silently=True)
        tweet_new_newsletter(self)
