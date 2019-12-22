"""luffy_boy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from api.views import course,img,user,shopping,payment
from django.views.static import serve
from django.conf import settings
urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^course/$', course.Course.as_view({'get':'get_list'})),
    url(r'^course_sub/$', course.CourseCategory.as_view()),
    url(r'^course/(?P<pk>\d+)', course.Course.as_view({'get':'get_detail'})),
    url(r'^get_imgs/', img.Img.as_view()),
    url(r'^login/$', user.Login.as_view()),
    url(r'^shopping/$',shopping.ShoppingCart.as_view()),
    url(r'^payment/$',payment.Payment.as_view()),
    url(r'^media/(?P<path>.*)', serve,{'document_root':settings.MEDIA_ROOT}),
]
