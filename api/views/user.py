from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from api.MySer import CourseSerializer, CourseDetailSerializer, CourseCategorySerializer
from api.utils.commonUtils import MyResponse
import uuid


class Login(APIView):
    def post(self, request, *args, **kwargs):
        response = MyResponse()
        name = request.data.get('name')
        pwd = request.data.get('pwd')
        user = models.UserInfo.objects.filter(name=name, pwd=pwd).first()
        if user:
            # 得去UserToken表中存数据
            # 生成一个随机字符串,不会重复
            token = uuid.uuid4()
            models.UserToken.objects.update_or_create(user=user, defaults={'token': token})
            response.token = token
            response.name=name
            response.msg = '登录成功'
        else:
            response.msg = '用户名或密码错误'
            response.status = '101'

        return Response(response.get_dic)
