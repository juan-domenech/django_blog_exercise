from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^blog/$', views.post_list ),
    url(r'^blog/(?P<id>\d+)/$', views.post_detail),
    ]
