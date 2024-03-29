# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-12-24 02:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('course_img', models.CharField(max_length=255)),
                ('brief', models.TextField(max_length=2048, verbose_name='课程概述')),
                ('level', models.SmallIntegerField(choices=[(0, '初级'), (1, '中级'), (2, '高级')], default=1)),
                ('pub_date', models.DateField(blank=True, null=True, verbose_name='发布日期')),
                ('period', models.PositiveIntegerField(default=7, verbose_name='建议学习周期(days)')),
                ('order', models.IntegerField(help_text='从上一个课程数字往后排', verbose_name='课程顺序')),
                ('status', models.SmallIntegerField(choices=[(0, '上线'), (1, '下线'), (2, '预上线')], default=0)),
            ],
            options={
                'verbose_name_plural': '专题课',
            },
        ),
        migrations.CreateModel(
            name='CourseDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hours', models.IntegerField(verbose_name='课时')),
                ('course_slogan', models.CharField(blank=True, max_length=125, null=True)),
                ('course', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.Course')),
                ('recommend_courses', models.ManyToManyField(blank=True, related_name='recommend_by', to='api.Course')),
            ],
            options={
                'verbose_name_plural': '课程详细',
            },
        ),
        migrations.CreateModel(
            name='PricePolicy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('valid_period', models.SmallIntegerField(choices=[(1, '1天'), (3, '3天'), (7, '1周'), (14, '2周'), (30, '1个月'), (60, '2个月'), (90, '3个月'), (180, '6个月'), (210, '12个月'), (540, '18个月'), (720, '24个月')])),
                ('price', models.FloatField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': '价格策略',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('image', models.CharField(max_length=128)),
                ('brief', models.TextField(max_length=1024)),
            ],
            options={
                'verbose_name_plural': '讲师',
            },
        ),
        migrations.AddField(
            model_name='coursedetail',
            name='teachers',
            field=models.ManyToManyField(to='api.Teacher', verbose_name='课程讲师'),
        ),
        migrations.AlterUniqueTogether(
            name='pricepolicy',
            unique_together=set([('content_type', 'object_id', 'valid_period')]),
        ),
    ]
