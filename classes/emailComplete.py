from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

class EmailComplete:

	fulfilled = {
		'subject':	'Promise complete. Status: Fulfilled!',
		'intro':	'Congratulations! {otherEmail} has marked your promise as "Fulfilled".',
		'new':		'Click below to make another promise or send a promise request:',
		'newTxt':	'Use the links below to make another promise or send a promise request:',
	}
	broken = {
		'subject':	'Promise complete. Status: Broken',
		'intro':	'{otherEmail} has marked your promise as "Broken".',
		'new':		'Click below to make another promise or send a promise request:',
		'newTxt':	'Use the links below to make another promise or send a promise request:',
	}

	@classmethod
	def sendEmail(cls, toEmail, otherEmail, url, contentDict):

		fromEmail = 'PromiseTracker<mail@PromiseTracker.com>'

		# set up email message
		plaintext = get_template('emailComplete.txt')
		html = get_template('emailComplete.html')

		# fetch class dictionary via string contentDict value
		params = getattr(cls, contentDict)
		params['url'] = url
		subject = params['subject']
		params['intro'] = params['intro'].format(otherEmail=otherEmail)

		textContent = plaintext.render(params)
		htmlContent = html.render(params)
		email = EmailMultiAlternatives(subject, textContent, fromEmail, [toEmail])
		email.attach_alternative(htmlContent, "text/html")

		# send email
		email.send()

