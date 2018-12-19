from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

class EmailApprove:

	senderIsPromisor = {
		'subject':	'Verify your promise.',
		'intro':	'You are making a promise to {otherEmail}.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'instrTxt':	'Click (or copy/paste) this link to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
	}
	receiverIsPromisee = {
		'subject':	'Someone is making a promise to you.',
		'info':		'PromiseTracker is a free online service that keeps a record of promises, and whether a promise is kept or not.',
		'intro':	'{otherEmail} is making a promise to you.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'instrTxt':	'Click (or copy/paste) this link to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
	}
	senderIsPromisee = {
		'subject':	'Verify your promise request.',
		'intro':	'You are making a promise to {otherEmail}.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'instrTxt':	'Click (or copy/paste) this link to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
	}
	receiverIsPromisor = {
		'subject':	'Someone requested you to make a promise.',
		'info':		'PromiseTracker is a free online service that keeps a record of promises, and whether a promise is kept or not.',
		'intro':	'{otherEmail} is requesting you to make a promise to them.',
		'instruct':	'Click here to review and approve the details of this promise:',
		'instrTxt':	'Click (or copy/paste) this link to review and approve the details of this promise:',
		'button':	'Review and Approve Promise',
	}

	@classmethod
	def sendEmail(cls, toEmail, otherEmail, url, contentDict):

		fromEmail = 'PromiseTracker<mail@PromiseTracker.com>'

		# set up email message
		plaintext = get_template('emailApprove.txt')
		html = get_template('emailApprove.html')

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

