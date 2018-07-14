from django.db import models

class profile(models.Model):
	name = models.CharField(max_length=120)
	description = models.TextField(default='description default text')

	def __str__(self):
		return self.name

	class Meta:
		db_table = "profile"
