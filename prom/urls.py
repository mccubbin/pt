from django.conf.urls import url, include
from . import views


urlpatterns = [
	url(
		r'^(?P<promid>[\w\d]+)/(?P<uid>[\w\d]+)/(?P<emailEncrypted>[\w\d=\-]+)$',
		views.manage,
		name='manage'
	),
	url(
		r'^(?P<promid>[\w\d]+)/$',
		views.public,
		name='public'
	),
]
