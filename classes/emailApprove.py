from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

class EmailApprove:

	senderIsPromisor = {
		'subject':	'Verify your promise.',
		'intro':	'You are making a promise to {otherEmail}.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
		# 'notify':	'You will be notified when the promisee has also approved the details of this promise.',
	}
	receiverIsPromisee = {
		'subject':	'Someone is making a promise to you.',
		'info':		'PromiseTracker is a free online service that keeps a record of promises, and whether a promise is kept or not.',
		'intro':	'{otherEmail} is making a promise to you.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
		# 'notify':	'You will be notified when this promise is approved by both parties and is active.',
	}
	senderIsPromisee = {
		'subject':	'Verify your promise request.',
		'intro':	'You are making a promise to {otherEmail}.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
		# 'notify':	'You will be notified when the promisor has also approved the details of this promise.',
	}
	receiverIsPromisor = {
		'subject':	'Someone requested you to make a promise.',
		'info':		'PromiseTracker is a free online service that keeps a record of promises, and whether a promise is kept or not.',
		'intro':	'{otherEmail} is requesting you to make a promise to them.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
		# 'notify':	'You will be notified when this promise is approved by both parties and is active.',
		# 'notify':	'After you approve this promise, the promisee can mark the promise as "Broken" or "Fulfilled" at their convenience.',
	}

	def __init__(self):
		pass

	@classmethod
	def sendEmail(cls, toEmail, otherEmail, url, contentDict):

		fromEmail = 'PromiseTracker<mail@PromiseTracker.com>'

		# set up email message
		plaintext = get_template('promEmail01.txt')
		html = get_template('promEmail01.html')

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

