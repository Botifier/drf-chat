from django.test import TestCase
from django.http import HttpRequest
from django.core.urlresolvers import reverse, resolve

from .views import index


class IndexTest(TestCase):

    def test_url_resolve_to_view(self):
        url = reverse('index')
        found = resolve(url)
        self.assertEqual(found.func, index)

    def test_index_returns_correct_html(self):
        request = HttpRequest()  
        response = index(request)  
        html = response.content.decode('utf8')  
        self.assertTrue(html.startswith('<html>'))  
        self.assertIn('<title>Chat demo app</title>', html)  
        self.assertTrue(html.endswith('</html>')) 