from rest_framework.views import APIView
from rest_framework.response import Response
from api import models

from api.utils.commonUtils import MyResponse
from rest_framework.viewsets import ViewSetMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from api.utils.MyAuth import LoginAuth
from api.utils.commonUtils import CommonException
from django_redis import get_redis_connection
import json


# 需要登录之后才能操作,写一个认证组件
class ShoppingCart(APIView):
    authentication_classes = [LoginAuth]
    conn = get_redis_connection()

    def post(self, request, *args, **kwargs):
        response = MyResponse()
        # 课程id,价格策略id
        # {"course_id": "1", "policy_id": "1"}
        # 放到redis中key值 shoppingcart_userid_courseid
        # 0 取出课程id,价格策略id
        course_id = str(request.data.get('course_id'))
        policy_id = str(request.data.get('policy_id'))
        # 1 校验课程是否合法
        try:
            course = models.Course.objects.get(pk=course_id)
            # 2 获取所有价格策略(通过课程拿出所有价格策略)
            policy_price_all = course.price_policy.all()
            # 3 从redis中取出当前登录用户的购物车
            shopping_byte = self.conn.get('shoppingcart_%s' % request.user.pk)
            if shopping_byte:
                shopping_cart = json.loads(shopping_byte)
            else:
                shopping_cart = {}
            # 循环构造出价格策略大字典
            policy = {}
            for policy_price in policy_price_all:
                '''
                {
                "period":3,
                "period_display":"3天",
                "price":200
                },
                '''
                policy_one = {
                    'period': policy_price.pk,
                    'period_display': policy_price.get_valid_period_display(),
                    'price': policy_price.price
                }
                policy[str(policy_price.pk)] = policy_one
            #     判断价格策略是否合法,不再字典中,就不合法
            if policy_id not in policy:
                # 不合法
                raise CommonException(102, '价格策略不合法,你不是人')
            # 判断传入的课程id是否在购物车中
            if course_id in shopping_cart:
                # 更新一下默认价格策略
                shopping_cart[course_id]['default_policy'] = policy_id
                response.msg = '更新成功'
            else:
                shopping_course = {
                    'title': course.name,
                    'img': course.course_img,
                    'default_policy': policy_id,
                    'policy': policy
                }

                # 添加到购物车
                shopping_cart[course_id] = shopping_course
                response.msg = '添加成功'
            #     写入redis
            self.conn.set('shoppingcart_%s' % request.user.pk, json.dumps(shopping_cart))

        except ObjectDoesNotExist as e:
            response.status = 101
            response.msg = '该课程不存在,你可能是爬虫'
        except CommonException as e:
            response.status = e.status
            response.msg = e.msg
        except Exception as e:
            response.status = 400
            response.msg = '未知错误'
            print(str(e))
        return Response(response.get_dic)

    def put(self, request, *args, **kwargs):
        response = MyResponse()
        # 0 取出课程id,价格策略id
        course_id = str(request.data.get('course_id'))
        policy_id = str(request.data.get('policy_id'))
        try:
            shopping_byte = self.conn.get('shoppingcart_%s' % request.user.pk)
            if shopping_byte:
                shopping_cart = json.loads(shopping_byte)
            else:
                shopping_cart = {}
            if course_id not in shopping_cart:
                raise CommonException(102, '要修改的课程不存在')
            course_detail = shopping_cart.get(course_id)
            if policy_id not in course_detail['policy']:
                raise CommonException(103, '价格策略不合法')
            course_detail['default_policy'] = policy_id
            response.msg = '修改成功'
            self.conn.set('shoppingcart_%s' % request.user.pk, json.dumps(shopping_cart))

        except ObjectDoesNotExist as e:
            response.status = 101
            response.msg = '该课程不存在,你可能是爬虫'
        except CommonException as e:
            response.status = e.status
            response.msg = e.msg
        except Exception as e:
            response.status = 400
            response.msg = '未知错误'
            print(str(e))
        return Response(response.get_dic)

    def get(self, request, *args, **kwargs):
        response = MyResponse()
        try:
            shopping_byte = self.conn.get('shoppingcart_%s' % request.user.pk)
            if shopping_byte:
                shopping_cart = json.loads(shopping_byte)
            else:
                shopping_cart = {}
            response.data = shopping_cart

        except Exception as e:
            response.status = 400
            response.msg = '未知错误'
            print(str(e))
        return Response(response.get_dic)

    def delete(self, request, *args, **kwargs):
        response = MyResponse()
        course_id = request.data.get('course_id')
        try:
            shopping_byte = self.conn.get('shoppingcart_%s' % request.user.pk)
            if shopping_byte:
                shopping_cart = json.loads(shopping_byte)
            else:
                shopping_cart = {}
            shopping_cart.pop(course_id, None)
            self.conn.set('shoppingcart_%s' % request.user.pk, json.dumps(shopping_cart))
        except Exception as e:
            response.status = 400
            response.msg = '未知错误'
            print(str(e))
        return Response(response.get_dic)
