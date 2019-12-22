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
class Payment(APIView):
    authentication_classes = [LoginAuth]
    conn = get_redis_connection()

    def post(self, request, *args, **kwargs):
        response = MyResponse()
        # {"course_list": [{"course_id": "1", "policy_id": "1"}, {"course_id": "2", "policy_id": "2"}]}
        # 取出前端传过来的数据
        course_list = request.data.get('course_list')
        try:
            # 1 构造出结算中心和全局优惠券 大字典
            payment_dic = {}
            global_coupon = {
                'coupon': {},
                'default_coupon': 0
            }
            # 2 拿出购物车
            shoppingcart = self.conn.get('shoppingcart_%s' % request.user.pk)
            # 三元表达式
            shoppingcart_dic = json.loads(shoppingcart) if shoppingcart else {}
            for course_in in course_list:
                # 判断这个id是否在购物车中,如果不在,直接抛异常
                course_in_id = course_in['course_id']
                if course_in_id not in shoppingcart_dic:
                    raise CommonException(101, '当前结算的课程不在购物车中')
                # 定义一个空的课程详情字典,内部放了个一个空的优惠券字典
                course_detail = {
                    'coupon': {},
                    'default_coupon': 0
                }
                course_detail.update(shoppingcart_dic[course_in_id])
                # 把刚刚构造的课程详情字典,放到结算中心大字典中
                payment_dic[course_in_id] = course_detail
            # 一次性查出当前用户的所有优惠券信息
            import datetime
            ctime = datetime.datetime.now()
            coupon_list = models.CouponRecord.objects.filter(user=request.user,
                                                             status=0,
                                                             coupon__valid_end_date__gte=ctime,
                                                             coupon__valid_begin_date__lte=ctime
                                                             )
            for coupon in coupon_list:
                # 所有优惠券:
                #     全站3张
                #     django3张--obj_id=1
                #     python3张--obj_id=2
                # 拿出优惠券类型数字
                coupon_type = coupon.coupon.coupon_type
                # 拿出优惠券类型文字描述
                coupon_type_display = coupon.coupon.get_coupon_type_display()
                object_id = coupon.coupon.object_id
                coupon_detail = {
                    "coupon_type": coupon_type,
                    "coupon_display": coupon_type_display,
                }
                #     coupon_detail={
                #         "coupon_type":1,
                #         "coupon_display":"满减券",
                #         "money_equivalent_value":10,
                #         "minimum_consume":100
                # }
                if coupon_type == '0':  # 立减
                    coupon_detail['money_equivalent_value'] = coupon.coupon.money_equivalent_value
                elif coupon_type == '1':  # 满减
                    coupon_detail['money_equivalent_value'] = coupon.coupon.money_equivalent_value
                    coupon_detail['minimum_consume'] = coupon.coupon.minimum_consume
                else:  # 折扣
                    coupon_detail['off_percent'] = coupon.coupon.off_percent
                # 全站优惠券
                if not object_id:
                    global_coupon['coupon'][str(coupon.pk)] = coupon_detail
                else:
                    # 课程优惠券
                    #
                    if payment_dic.get(str(object_id), None):
                        payment_dic[str(object_id)]['coupon'][str(coupon.pk)] = coupon_detail

            #     存到redis
            self.conn.set('payment_%s' % request.user.pk, json.dumps(payment_dic))
            self.conn.set('globalcoupon_%s' % request.user.pk, json.dumps(global_coupon))
            response.msg = '加入成功'
        except CommonException as e:
            response.status = e.status
            response.msg = e.msg
        # except Exception as e:
        #     response.status = 400
        #     response.msg = '未知错误'
        #     print(str(e))
        return Response(response.get_dic)


#     删除,新增,修改


# 结算中心:
class Account(APIView):
    authentication_classes = [LoginAuth]
    conn = get_redis_connection()

    def post(self, request, *args, **kwargs):
        response = MyResponse()
        # {
        #     "price": 600
        #     "bely": 100
        # }
        # 取出前端传过来的数据
        price_in = request.data.get('price')
        bely = request.data.get('bely')
        try:
            # 取出结算中心的字典,全局优惠券大字典
            payment_bytes = self.conn.get('payment_%s' % request.user.pk)
            payment_dic = json.loads(payment_bytes) if payment_bytes else {}
            global_coupon_bytes = self.conn.get('globalcoupon_%s' % request.user.pk)
            global_coupon = json.loads(global_coupon_bytes) if global_coupon_bytes else {}
            # 定义一个列表存储所有课程优惠完成之后的价格,以后计算总价格直接sum(列表)
            list_price=[]
            for course_id, course_detail in payment_dic.items():
                # 取出默认价格策略，取出默认价格，取出默认优惠券id
                default_policy = course_detail['default_policy']
                default_price = course_detail['policy'][str(default_policy)]['price']
                default_coupon_id = course_detail['default_coupon']

                # 如果是0 ,没有选择优惠券,if内的不需要走
                if default_coupon_id != '0':
                    default_coupon_detail = course_detail['coupon'][str(default_coupon_id)]
                    default_price=self.account(default_price,default_coupon_detail)
                list_price.append(default_price)
            #计算总价格,也有优惠券
            global_coupon_id=global_coupon['default_coupon']
            global_coupon_detail=global_coupon['coupon'][str(global_coupon_id)]
            final_price=self.account(sum(list_price),global_coupon_detail)

        #     判断贝利是否合法
            if int(bely) >request.user.bely:
                raise CommonException(103,'贝利数不合法')
            final_price=final_price-int(bely)/10
            request.user.bely=request.user.bely-int(bely)
            request.user.save()
            if not final_price==float(price_in):
                raise CommonException(104,'传入的价格不合法')
            # 生成订单,往订单表插入一条数据
            if final_price<=0:
                final_price=0
            else:
                # 构造支付宝链接
                # 拼凑支付宝url
                alipay = ali()
                import time
                # 生成支付的url
                query_params = alipay.direct_pay(
                    subject="路飞学成课程",  # 商品简单描述
                    out_trade_no="x2" + str(time.time()),  # 商户订单号
                    total_amount=final_price,  # 交易金额(单位: 元 保留俩位小数)
                )
                pay_url = "https://openapi.alipaydev.com/gateway.do?{}".format(query_params)
                response.url = pay_url
        except CommonException as e:
            response.status = e.status
            response.msg = e.msg
        except Exception as e:
            response.status = 400
            response.msg = '未知错误'
            print(str(e))
        return Response(response.get_dic)

    def account(self, default_price, default_coupon_detail):
        coupon_type = default_coupon_detail['coupon_type']
        if coupon_type == 0:  # 立减
            default_price = default_price - default_coupon_detail['money_equivalent_value']
        elif coupon_type == 1:  # 满减
            if default_price >= default_coupon_detail['minimum_consume']:
                default_price = default_price - default_coupon_detail['money_equivalent_value']
            else:
                raise CommonException(102, '不满足最低消费金额')
        else:
            default_price = default_price * default_coupon_detail['off_percent'] / 100

        return default_price
