import os
import io
import unittest
import database
from app import app

class ModelGalleryTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        database.init_db()

    def test_01_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Нещодавно додані моделі'.encode('utf-8'), response.data)
        self.assertIn('GALLERY'.encode('utf-8'), response.data)

    def test_02_gallery_tab(self):
        response = self.client.get('/gallery')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Галерея 3D Моделей'.encode('utf-8'), response.data)

    def test_03_search_by_name(self):
        response = self.client.get('/gallery?q=шолом')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Шолом'.encode('utf-8'), response.data)

    def test_04_search_by_tag(self):
        response = self.client.get('/gallery?tag=sci-fi')
        self.assertEqual(response.status_code, 200)
        self.assertIn('sci-fi'.encode('utf-8'), response.data)

    def test_05_api_search(self):
        response = self.client.get('/api/search?q=качка')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any('Качечка' in item['title'] or 'Duck' in item['title'] for item in data))

    def test_06_model_detail(self):
        # Отримуємо першу доступну модель
        recent = database.get_recent_models(1)
        self.assertTrue(len(recent) > 0)
        model_id = recent[0]['id']
        
        response = self.client.get(f'/model/{model_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Фотогалерея моделі'.encode('utf-8'), response.data)

    def test_07_add_model_with_gallery_photos(self):
        import uuid
        unique_name = f"Тестова Ракета {uuid.uuid4().hex[:6]}"
        data = {
            'title': unique_name,
            'category': 'Транспорт та Техніка',
            'description': 'Тестовий опис для нової 3D ракети',
            'tags': 'ракета, космос, тест',
            'author': 'Tester',
            'poly_count': '5,000',
            'thumbnail': (io.BytesIO(b'fake-image-bytes'), 'test_thumb.jpg'),
            'gallery_photos': [
                (io.BytesIO(b'fake-photo-1'), 'render_1.jpg'),
                (io.BytesIO(b'fake-photo-2'), 'render_2.jpg'),
                (io.BytesIO(b'fake-photo-3'), 'wireframe.jpg')
            ]
        }
        response = self.client.post('/add', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(unique_name.encode('utf-8'), response.data)
        
        # Перевірка бази даних
        models = database.get_all_models(search_query=unique_name)
        self.assertEqual(len(models), 1)
        test_model = models[0]
        self.assertEqual(test_model['title'], unique_name)
        self.assertEqual(test_model['photo_count'], 3)
        
        photos = database.get_model_photos(test_model['id'])
        self.assertEqual(len(photos), 3)

        # Тест видалення
        del_resp = self.client.post(f'/model/{test_model["id"]}/delete', follow_redirects=True)
        self.assertEqual(del_resp.status_code, 200)
        
        # Перевіряємо, що модель видалено з бази
        self.assertIsNone(database.get_model_by_id(test_model['id']))

if __name__ == '__main__':
    unittest.main()
