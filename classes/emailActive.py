from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

class EmailActive:

	promisor = {
		'subject':	'Promise is now active!',
		'intro':	'{otherEmail} has approved your promise.',
		'button':	'View Promise',
		'notify':	'It is now up to you to do what you have promised.',
		'notify2':	'The promisee must decide to mark the promise as "Broken" or "Fulfilled". When they do, we will notify you.',
	}
	promisee = {
		'subject':	'Promise is now active!',
		'intro':	'{otherEmail} has approved this promise.',
		'instruct':	'When the promisor has kept (or broken) this promise, please go to this link and mark the promise as "Fulfilled" or "Broken".',
		'button':	'Mark Promise Status',
	}
	promiseeReference = {
		'subject':	'Promise is now active!',
		'intro':	'You have approved this promise.',
		'instruct':	'Whenever you are ready, please go to this link and mark the promise as "Fulfilled" or "Broken".',
		'button':	'Mark Promise Status',
	}

	@classmethod
	def sendEmail(cls, toEmail, otherEmail, url, contentDict):

		fromEmail = 'PromiseTracker<mail@PromiseTracker.com>'

		# set up email message
		plaintext = get_template('EmailActive.txt')
		html = get_template('EmailActive.html')

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

