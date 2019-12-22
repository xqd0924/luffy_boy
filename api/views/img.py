from rest_framework.views import APIView
from rest_framework.response import Response


class Img(APIView):
    def get(self, request, *args, **kwargs):
        return Response(['http://127.0.0.1:8000/media/1.png', 'http://127.0.0.1:8000/media/2.png',
                         'http://127.0.0.1:8000/media/1.png'])

