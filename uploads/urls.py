from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from core import views


urlpatterns = [
    url(r'^$', views.home, name='home'), 
    url(r'^user/$',views.user,name="user"),
    url(r'^form/$', views.model_form_upload, name='model_form_upload'),
    url(r'^user/mypass/$', views.mypass,name='mypass'),  
    url(r'^user/forget_pass/$',views.forget_pass,name='forget_pass'), 
    url(r'^user/qrcode_miss/$',views.qrcode_miss,name='qrcode_miss'),
    url(r'^user_req/$',views.user_req, name="user_req"),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
