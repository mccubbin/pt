from django import forms
from django.contrib.admin import widgets
#from datetime import datetime

from classes.encryption import Encryption
from prom.models import blacklist



class promiseForm(forms.Form):

	emailpromer = forms.EmailField(
		required=True,
		label="Your email",
		# widget=forms.TextInput(attrs={'size':10, 'max_length':20}),
	)
	emailpromee = forms.EmailField(
		required=True,
		label="Email of recipient",
	)
	public = forms.BooleanField(
		label="&nbsp;Public",
		required=False,
		widget=forms.CheckboxInput(attrs={
		}),
	)
	details = forms.CharField(
		required=True,
		widget=forms.Textarea(attrs={
			'rows':3,
			'placeholder': 'text',
		}),
		max_length=2000,
		label="Promise details",
	)
	# privacy = forms.ChoiceField(
	# 	choices=RADIO,
	# 	widget=forms.RadioSelect(),
	# )
	# compdate = forms.DateTimeField(
	# 	widget=widgets.AdminSplitDateTime(),
	# 	#input_formats = ('%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d'),
	# 	required=False,
	# 	label="Completion Date",
	# )

	def clean(self):
		cleaned_data = super(promiseForm, self).clean()
		emailpromer = cleaned_data.get('emailpromer')
		emailpromee = cleaned_data.get('emailpromee')

		if emailpromer == None or emailpromee == None:
			raise forms.ValidationError('Email addresses must be valid.')

		emailpromer = emailpromer.lower()
		emailpromee = emailpromee.lower()

		if emailpromer and emailpromee and (emailpromer == emailpromee):
			#self._errors['emailpromee'] = self.error_class(['Emails cannot be the same.'])
			#del self.cleaned_data['emailpromee']
			raise forms.ValidationError('Emails must be different.')

		if isBlacklisted(emailpromer):
			raise forms.ValidationError(emailpromer + ' is blacklisted.')
		if isBlacklisted(emailpromee):
			raise forms.ValidationError(emailpromee + ' is blacklisted.')

		# LOWERCASE email addresses before going back to view
		cleaned_data["emailpromer"] = emailpromer
		cleaned_data["emailpromee"] = emailpromee

		return cleaned_data

class promerForm(promiseForm):

	PROMISETEXT = (
		'I, [your name], promise to go to brunch this Saturday '
		'with Mark and Lana. '
		'(even though I really don\'t want to go)'
	)

	emailpromer = forms.EmailField(
		required=True,
		label="Your email",
		# widget=forms.TextInput(attrs={'size':10, 'max_length':20}),
	)
	emailpromee = forms.EmailField(
		required=True,
		label="Email of recipient",
	)
	details = forms.CharField(
		required=True,
		widget=forms.Textarea(attrs={
			'rows':3,
			'placeholder': PROMISETEXT,
		}),
		max_length=2000,
		label="Promise details",
	)


class promeeForm(promiseForm):

	PROMISETEXT = (
		'I, [name of promisor], promise to pay Kevin '
		'the money I owe him by this Saturday.'
	)

	emailpromee = forms.EmailField(
		required=True,
		label="Your email",
	)
	emailpromer = forms.EmailField(
		required=True,
		label="Promisor email",
	)
	details = forms.CharField(
		required=True,
		widget=forms.Textarea(attrs={
			'rows':3,
			'placeholder': PROMISETEXT,
		}),
		max_length=2000,
		label="Promise details",
	)


#####################################################################
# Check if email has been blacklisted
#####################################################################
def isBlacklisted(email):
        encemail = Encryption.encrypt(email)
        Blacklist = blacklist.objects.filter(email=encemail).first()

        if Blacklist:
                return True
        else:
                return False

