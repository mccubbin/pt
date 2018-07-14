from django.conf.urls import url, include
from . import views
from django.views.generic import ListView, DetailView
from prom.models import promise


urlpatterns = [
	url(
		r'^$',
		views.RecordView.as_view(),
		name='record'
	),
]

'''
	url(
		r'^$',
		ListView.as_view(
			queryset=promise.objects.all().order_by("-compdate")[:25],
			template_name="record.html"
		),
		name='record'
	),
	url(
		r'^(?P<pk>[\w\d]+)$',
		DetailView.as_view(
						model = Post,
						template_name = "post.html"
		)
	),
'''

