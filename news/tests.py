from django.test import TestCase
from rest_framework.test import APIClient
from .models import CustomUser, Publisher, Article


class APITestCase(TestCase):
    """Test case for API endpoints with user roles."""
    def setUp(self):
        self.client = APIClient()
        self.reader = CustomUser.objects.create_user(
            username='reader', password='pass', role='reader'
        )
        self.journalist = CustomUser.objects.create_user(
            username='journalist', password='pass', role='journalist'
        )
        self.editor = CustomUser.objects.create_user(
            username='editor', password='pass', role='editor'
        )
        self.publisher = Publisher.objects.create(name='TestPub')
        self.article = Article.objects.create(
            title='Test', content='Content', publisher=self.publisher,
            journalist=self.journalist, approved=True
        )
        self.reader.subscribed_publishers.add(self.publisher)

    def test_get_articles_reader(self):
        """Tests article retrieval for a reader user."""
        self.client.force_authenticate(self.reader)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_get_articles_unauthorized(self):
        self.client.force_authenticate(self.journalist)
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, 403)

    def test_create_article_journalist(self):
        self.client.force_authenticate(self.journalist)
        data = {'title': 'New Article', 'content': 'Content',
                'publisher': self.publisher.id}
        response = self.client.post('/api/articles/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_article_unauthorized(self):
        self.client.force_authenticate(self.editor)
        data = {'title': 'New Article', 'content': 'Content',
                'publisher': self.publisher.id}
        response = self.client.post('/api/articles/', data, format='json')
        self.assertEqual(response.status_code, 403)

    def test_list_publisher_articles(self):
        self.client.force_authenticate(self.editor)
        response = self.client.get(
            f'/api/articles/publisher/{self.publisher.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_approve_article_editor(self):
        unapproved_article = Article.objects.create(
            title='Unapproved', content='Content', publisher=self.publisher,
            journalist=self.journalist, approved=False
        )
        self.client.force_authenticate(self.editor)
        data = {'approved': True}
        response = self.client.post(
            f'/api/articles/{unapproved_article.id}/approve/',
            data, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Article.objects.get(id=unapproved_article.id).approved)

    def test_approve_article_unauthorized(self):
        unapproved_article = Article.objects.create(
            title='Unapproved', content='Content', publisher=self.publisher,
            journalist=self.journalist, approved=False
        )
        self.client.force_authenticate(self.journalist)
        data = {'approved': True}
        response = self.client.post(
            f'/api/articles/{unapproved_article.id}/approve/',
            data, format='json'
        )
        self.assertEqual(response.status_code, 403)
