from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from api.MySer import CourseSerializer, CourseDetailSerializer,CourseCategorySerializer
from api.utils.commonUtils import MyResponse
from rest_framework.viewsets import ViewSetMixin
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class Course(ViewSetMixin, APIView):

    def get_list(self, request, *args, **kwargs):
        response = MyResponse()
        # 取出要过滤的条件
        param=request.GET.get('sub_category',None)
        course_list = models.Course.objects.all()
        param=int(param)
        if param:
            course_list=course_list.filter(category_id=param)
        course_ser = CourseSerializer(instance=course_list, many=True)
        response.msg = '查询成功'
        response.data = course_ser.data

        return Response(response.get_dic)

    def get_detail(self, request, pk, *args, **kwargs):
        response = MyResponse()

        try:
            # 因为查的是课程详情表,传过来的pk 是课程表的主键
            course_detail = models.CourseDetail.objects.get(course_id=pk)
            course_detail_ser = CourseDetailSerializer(instance=course_detail, many=False)
            response.data = course_detail_ser.data
        except ObjectDoesNotExist as e:
            response.status = 101
            response.msg = '您要查询的课程不存在'
        except Exception as e:
            response.status = 105
            if settings.DEBUG:
                response.msg = str(e)
            else:
                response.msg = '未知错误'

        return Response(response.get_dic)


class CourseCategory(APIView):
    def get(self,request,*args,**kwargs):
        response = MyResponse()
        category_list=models.CourseCategory.objects.all()
        ser=CourseCategorySerializer(instance=category_list,many=True)
        response.data=ser.data

        return Response(response.get_dic)
