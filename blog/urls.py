from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^$', views.no_path ),
    url(r'^blog/$', views.post_list ),
    url(r'^blog/(?P<id>\d+)/$', views.post_detail ),
    url(r'^post/new/$', views.new_post, name='new_post' ),
    url(r'^post/edit/(?P<pk>\d+)/$', views.edit_post, name='edit_post' ),
    ]
