from rest_services.views import BatchViewSet
from rest_framework.test import (APIRequestFactory, APITestCase, APIClient)
import datetime


class BatchViewSetTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        with open('media/test/sample_ip.csv') as file:
            self.data = {'batch_name': 'test', 'source_file_name': file, 'file_format': 'C', 'batch_status': 'INIT', 'created_at': datetime.datetime.now()}
            self.client = APIClient()
            self.url = '/api/batches/'
            self.client.credentials(HTTP_X_USER_ID='test')
            self.response = self.client.post(self.url, self.data, format='multipart')

    def test_batch_retrieve(self):
        retrieve_view = BatchViewSet.as_view({'get': 'retrieve'})
        request = self.factory.get("")
        response = retrieve_view(request, pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['batch_id'], 1)

    def test_create(self):
        self.assertEqual(self.response.status_code, 201)

    def test_list(self):
        list_view = BatchViewSet.as_view({'get': 'list'})
        request = self.factory.get("")
        response = list_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text='batch_id')
