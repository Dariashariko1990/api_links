import datetime

from random import randrange

import redis
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


# Connect to our Redis instance
from api.services import validate, extract_domain

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                   port=settings.REDIS_PORT, db=0)


class LinksView(APIView):
    """ Endpoint for posting a list of visited links."""
    def post(self, request, *args, **kwargs):
        data = request.data
        links = data[list(data.keys())[0]]
        data = {}

        for link in links:
            if validate(link):
                ts = datetime.datetime.now().timestamp()
                rndm = randrange(0, 10000)

                # Add random data to link to ensure uniqueness of value before inserting into Redis sorted set
                link = f'{link}/{rndm}'
                data[link] = ts
            else:
                return Response({'status': 'Не валидный запрос, введите валидный url.'},
                                status=status.HTTP_400_BAD_REQUEST)

        redis_instance.zadd("links", data)

        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)


class DomainStatView(APIView):
    """ Endpoint for retrieving a list of unique visited domains in specified period of time."""
    def get(self, request, *args, **kwargs):

        if request.GET.get('from') is None or request.GET.get('to') is None:
            return Response({'status': 'Не валидный запрос, введите валидные параметры запроса.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            start = int(request.GET.get('from'))
            end = int(request.GET.get('to'))
        except ValueError:
            return Response({'status': 'Не валидный запрос, введите валидные параметры запроса.'},
                            status=status.HTTP_400_BAD_REQUEST)

        name = "links"
        data = redis_instance.zrangebyscore(name, start, end)
        unique_domains = {extract_domain(link.decode("utf-8")) for link in data}

        response = {
            'domains': unique_domains,
            'status': "ok",
        }
        return Response(response)

