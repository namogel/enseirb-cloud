from django.conf.urls import patterns, include, url
from django.contrib import admin
from app import views

urlpatterns = patterns('',
    
    url(r'^$', views.home),
    url(r'^home$', views.home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/?$', views.login_user),
    url(r'^accounts/logout$', views.logout_user),
    url(r'^file/upload$', views.upload_file),
    url(r'^file/delete$', views.delete_file),
    url(r'^tree/new$', views.new_folder),
    url(r'^tree/update/move$', views.move_file),
)
