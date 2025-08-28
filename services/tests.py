from django.test import TestCase
from django.urls import reverse
from core.models import Category, Tag
from .models import Service


class ServiceViewsTestCase(TestCase):
	def setUp(self):
		# категории и теги
		self.cat = Category.objects.create(name='Тестовая', slug='test-cat')
		self.tag1 = Tag.objects.create(name='Тег1', slug='tag1')

		# услуги
		for i in range(1, 7):
			s = Service.objects.create(
				title=f'Service {i}', slug=f'service-{i}',
				category=self.cat,
				short_desc='short', description='desc',
				price_adult=1000 + i,
				price_child=500 + i,
				is_active=True,
			)
			# добавить тег к первой услуге
			if i == 1:
				s.tags.add(self.tag1)

		# пометим первый сервис популярным если есть поле
		try:
			s0 = Service.objects.first()
			if hasattr(s0, 'is_popular'):
				s0.is_popular = True
				s0.save()
		except Exception:
			pass

	def test_service_list_context(self):
		url = reverse('services:list')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		# контекст
		self.assertIn('categories', resp.context)
		self.assertIn('tags', resp.context)
		self.assertIn('popular_services', resp.context)

		categories = resp.context['categories']
		self.assertTrue(any(c.slug == 'test-cat' for c in categories))

		tags = resp.context['tags']
		self.assertTrue(any(t.slug == 'tag1' for t in tags))

		popular = resp.context['popular_services']
		# popular — список, длина не больше 5
		self.assertIsInstance(popular, list)
		self.assertLessEqual(len(popular), 5)
