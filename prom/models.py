from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class promise(models.Model):
	STATUS_CHOICES = (
		('draft', 'Draft'),
		('pending', 'Pending'),
		('broken', 'Broken'),
		('fulfilled', 'Fulfilled'),
		('delete', 'Delete'),
	)
	PRIVACY_CHOICES = (
		('private', 'Private'),
		('public', 'Public'),
	)

	promid = models.AutoField(auto_created=True, primary_key=True, serialize=False)
	cdate = models.DateTimeField(default=timezone.now)
	mdate = models.DateTimeField(default=timezone.now)
	status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='draft')
	privacy = models.CharField(choices=PRIVACY_CHOICES, max_length=20, default='private')
	details = models.CharField(max_length=2000)
	compdate = models.DateTimeField(null=True, blank=True)
	promerid = models.ForeignKey(User, on_delete=models.PROTECT, related_name='promerid', null=True, blank=True)
	promerapprdate = models.DateTimeField(null=True, blank=True)
	promeeid = models.ForeignKey(User, on_delete=models.PROTECT, related_name='promeeid', null=True, blank=True)
	promeeapprdate = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.details

	class Meta:
		db_table = "promise"


class blacklist(models.Model):
	email = models.CharField(max_length=254)
	cdate = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.email

	class Meta:
		db_table = "blacklist"
