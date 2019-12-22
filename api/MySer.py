from rest_framework import serializers
from api import models


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'name', 'course_img']

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseCategory
        fields = '__all__'

class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseDetail
        fields = '__all__'

    course_name = serializers.CharField(source='course.name')
    recommend_courses = serializers.SerializerMethodField()

    def get_recommend_courses(self, obj):
        # obj.recommend_courses.all()拿到的是该课程所有的推荐课程,queryset对象,放了一个个的课程对象
        return [{'id': course.pk, 'name': course.name} for course in obj.recommend_courses.all()]

    teachers=serializers.SerializerMethodField()

    def get_teachers(self, obj):
        return [{'id': teacher.pk, 'name': teacher.name,'brief':teacher.brief} for teacher in obj.teachers.all()]
