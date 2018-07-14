"""prom URL Configuration

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
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from home import views as homeviews
from prom import views as promviews
from profiles import views as profileviews

urlpatterns = [
	url(
		r'^',
		include('home.urls')
	),
	url(
		r'^admin/',
		admin.site.urls
	),
	url(
		r'^record/',
		include('records.urls')
	),
	url(
		r'^profile/$',
		profileviews.userProfile,
		name='profile'
	),
	url(
		r'^example/$',
		homeviews.example,
		name='example'
	),
	url(
		r'^accounts/',
		include('allauth.urls')
	),
	url(
		r'^(?P<who>make)/$', #if make: who='make'
		promviews.PromView.as_view(),
	),
	url(
		r'^(?P<who>send)/$', #if send: who='send'
		promviews.PromView.as_view(),
	),
	url(
		r'^crm/',
		include('prom.urls')
	),
	url(
		r'^bl/(?P<encemail>[\w\d=\-]+)$',
		promviews.blacklistEmail,
		name='blacklist'
	),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
