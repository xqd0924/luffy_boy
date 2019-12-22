from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.contrib.contenttypes.fields import GenericRelation


# Create your models here.
class UserInfo(models.Model):
    name = models.CharField(max_length=64)
    pwd = models.CharField(max_length=64)
    bely=models.IntegerField(default=100)
    def __str__(self):
        return self.name


class UserToken(models.Model):
    user = models.OneToOneField(to='UserInfo')
    token = models.CharField(max_length=64)
    # time=models.DateTimeField(auto_now=True)


class CourseCategory(models.Model):
    nid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Course(models.Model):
    """专题课程"""

    # category_choices = ((0, 'go'), (1, 'Python'), (2, 'Linux'))
    # category = models.SmallIntegerField(choices=category_choices, default=1)
    category = models.ForeignKey(to='CourseCategory', to_field='nid', null=True)

    # unique=True 唯一性约束
    name = models.CharField(max_length=128, unique=True)
    course_img = models.CharField(max_length=255)
    brief = models.TextField(verbose_name="课程概述", max_length=2048)

    level_choices = ((0, '初级'), (1, '中级'), (2, '高级'))
    # 默认值为1 ,中级
    level = models.SmallIntegerField(choices=level_choices, default=1)
    pub_date = models.DateField(verbose_name="发布日期", blank=True, null=True)
    period = models.PositiveIntegerField(verbose_name="建议学习周期(days)", default=7)
    # help_text 在admin中显示的帮助信息
    order = models.IntegerField("课程顺序", help_text="从上一个课程数字往后排")

    status_choices = ((0, '上线'), (1, '下线'), (2, '预上线'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    # 用于GenericForeignKey反向查询，不会生成表字段，切勿删除
    price_policy = GenericRelation("PricePolicy")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "专题课"


class CourseDetail(models.Model):
    """课程详情页内容"""
    course = models.OneToOneField("Course", on_delete=models.CASCADE)
    hours = models.IntegerField("课时")
    # 课程的标语 口号
    course_slogan = models.CharField(max_length=125, blank=True, null=True)
    # video_brief_link = models.CharField(verbose_name='课程介绍', max_length=255, blank=True, null=True)
    # why_study = models.TextField(verbose_name="为什么学习这门课程")
    # what_to_study_brief = models.TextField(verbose_name="我将学到哪些内容")
    # career_improvement = models.TextField(verbose_name="此项目如何有助于我的职业生涯")
    # prerequisite = models.TextField(verbose_name="课程先修要求", max_length=1024)
    # 推荐课程
    # related_name 基于对象的反向查询,用于替换表名小写_set
    recommend_courses = models.ManyToManyField("Course", related_name="recommend_by", blank=True)
    teachers = models.ManyToManyField("Teacher", verbose_name="课程讲师")

    def __str__(self):
        return "%s" % self.course

    class Meta:
        verbose_name_plural = "课程详细"


class PricePolicy(models.Model):
    """价格与有课程效期表"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # 关联course or degree_course
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # course = models.ForeignKey("Course")
    valid_period_choices = ((1, '1天'), (3, '3天'),
                            (7, '1周'), (14, '2周'),
                            (30, '1个月'),
                            (60, '2个月'),
                            (90, '3个月'),
                            (180, '6个月'), (210, '12个月'),
                            (540, '18个月'), (720, '24个月'),
                            )
    valid_period = models.SmallIntegerField(choices=valid_period_choices)
    price = models.FloatField()

    class Meta:
        unique_together = ("content_type", 'object_id', "valid_period")
        verbose_name_plural = "价格策略"

    def __str__(self):
        return "%s(%s)%s" % (self.content_object, self.get_valid_period_display(), self.price)


class Teacher(models.Model):
    """讲师、导师表"""
    name = models.CharField(max_length=32)
    image = models.CharField(max_length=128)
    brief = models.TextField(max_length=1024)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "讲师"


class Coupon(models.Model):
    """优惠券生成规则"""
    name = models.CharField(max_length=64, verbose_name="活动名称")
    brief = models.TextField(blank=True, null=True, verbose_name="优惠券介绍")
    coupon_type_choices = ((0, '立减券'), (1, '满减券'), (2, '折扣券'))
    coupon_type = models.SmallIntegerField(choices=coupon_type_choices, default=0, verbose_name="券类型")

    money_equivalent_value = models.IntegerField(verbose_name="等值货币", blank=True, null=True)
    off_percent = models.PositiveSmallIntegerField("折扣百分比", help_text="只针对折扣券，例7.9折，写79", blank=True, null=True)
    minimum_consume = models.PositiveIntegerField("最低消费", default=0, help_text="仅在满减券时填写此字段")

    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField("绑定课程", blank=True, null=True, help_text="可以把优惠券跟课程绑定")
    content_object = GenericForeignKey('content_type', 'object_id')

    quantity = models.PositiveIntegerField("数量(张)", default=1)
    open_date = models.DateField("优惠券领取开始时间")
    close_date = models.DateField("优惠券领取结束时间")
    valid_begin_date = models.DateField(verbose_name="有效期开始时间", blank=True, null=True)
    valid_end_date = models.DateField(verbose_name="有效结束时间", blank=True, null=True)
    coupon_valid_days = models.PositiveIntegerField(verbose_name="优惠券有效期（天）", blank=True, null=True,
                                                    help_text="自券被领时开始算起")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "31. 优惠券生成规则"

    def __str__(self):
        return "%s(%s)" % (self.get_coupon_type_display(), self.name)


class CouponRecord(models.Model):
    """优惠券发放、消费纪录"""
    # 跟优惠券生成规则是一对多的关系
    coupon = models.ForeignKey("Coupon", on_delete=models.CASCADE)
    number = models.CharField(max_length=64)
    # 跟user什么关系?一对多,一个用户有多张优惠券,一张优惠券只能给一个用户
    user = models.ForeignKey("UserInfo", verbose_name="拥有者", on_delete=models.CASCADE)
    status_choices = ((0, '未使用'), (1, '已使用'), (2, '已过期'))
    status = models.SmallIntegerField(choices=status_choices, default=0)
    get_time = models.DateTimeField(verbose_name="领取时间", help_text="用户领取时间")
    used_time = models.DateTimeField(blank=True, null=True, verbose_name="使用时间")

    class Meta:
        verbose_name_plural = "32. 优惠券发放、消费纪录"

    def __str__(self):
        return '%s-%s-%s' % (self.user, self.number, self.status)
