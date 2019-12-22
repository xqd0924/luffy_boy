from rest_framework.authentication import BaseAuthentication
from api import models
from rest_framework.exceptions import AuthenticationFailed


class LoginAuth(BaseAuthentication):
    def authenticate(self, request):
        token = request.GET.get('token')
        ret = models.UserToken.objects.filter(token=token).first()
        if ret:
            # 有值说明认证通过,返回两个值
            return ret.user, ret
        else:
            raise AuthenticationFailed('认证失败,没有登录')
