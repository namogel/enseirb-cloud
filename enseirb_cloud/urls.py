from django.conf.urls import patterns, include, url
from django.contrib import admin
from app import views

urlpatterns = patterns('',
    
    url(r'^$', views.home),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/?$', views.login_user),
    url(r'^accounts/logout$', views.logout_user),
)
