from django import forms
from django.contrib.admin import widgets
import re
#from datetime import datetime

class searchForm(forms.Form):

	search = forms.CharField(
		required = True,
		max_length = 254,
		widget = forms.EmailInput(
			attrs={
				'placeholder': 'Enter email address',
				'class':'form-control'
			}
		),
	)

	def clean(self):
		cleaned_data = super(searchForm, self).clean()
		search = cleaned_data.get('search').lower()

		if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", search):
			raise forms.ValidationError('Email address must be valid.')

		# LOWERCASE email addresses before going back to view
		cleaned_data["search"] = search
		
		return cleaned_data


