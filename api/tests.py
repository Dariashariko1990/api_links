import datetime
from unittest.mock import patch

import fakeredis
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import api.views


LINKS_URL = reverse('links')
DOMAINS_URL = reverse('domain_stat')


class PublicLinksApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        redis_patcher = patch('api.views.redis_instance', fakeredis.FakeStrictRedis())
        self.redis = redis_patcher.start()

    def test_post_valid_links(self):
        """ Test that valid post request will return HTTP_201_CREATED. """
        payload = {
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        }

        res = self.client.post(LINKS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_links_saved(self):
        """ Test that post request results in links saved to our redis instance. """
        payload = {
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
            ]
        }
        links_count = len(payload["links"])
        res = self.client.post(LINKS_URL, payload, format='json')

        redis_links = []

        for link in api.views.redis_instance.zrevrange("links", 0, links_count - 1):
            link = link.decode("utf-8")
            redis_links.append("/".join(link.split('/')[:-1]))

        self.assertEqual(redis_links[::-1], payload["links"])

    def test_post_invalid_links(self):
        """ Test that request with invalid urls passed in request body will return 400_BAD_REQUEST. """
        for link in ("123", "ya", 123, ""):
            payload = {"links": [
                link,
            ]
            }

            res = self.client.post(LINKS_URL, payload, format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden_methods(self):
        """ Test that endpoint is not permitting GET, PUT or DELETE operations. """
        res = self.client.get(LINKS_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        res = self.client.delete(LINKS_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        res = self.client.put(LINKS_URL, {"links": ["ya.ru"]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class PublicDomainApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_domains(self):
        """ Test retrieve domains in specified period. """
        end = int(datetime.datetime.now().timestamp())
        start = int((datetime.datetime.now() + datetime.timedelta(days=7)).timestamp())

        res = self.client.get(DOMAINS_URL, {'from': start, 'to': end})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_invalid_query_params(self):
        """ Test that request with invalid type of query params (string) will return 400_BAD_REQUEST. """
        for param in (("", ""), ("stringparam", "str")):
            res = self.client.get(DOMAINS_URL, {'from': param[0], 'to': param[1]})
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_query_params(self):
        """ Test that request with no query params will return 400_BAD_REQUEST. """
        res = self.client.get(DOMAINS_URL)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_forbidden_methods(self):
        """ Test that endpoint is not permitting POST, PUT or DELETE operations. """

        res = self.client.post(DOMAINS_URL, {"links": ["ya.ru"]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        res = self.client.delete(DOMAINS_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        res = self.client.put(DOMAINS_URL, {"links": ["ya.ru"]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
