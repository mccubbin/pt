#from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views import View
import base36
import datetime
from django.utils import timezone
import pytz


from classes.encryption import Encryption
from classes.emailApprove import EmailApprove
from classes.emailActive import EmailActive
from classes.emailComplete import EmailComplete

from django.db import connection
from prom.models import promise, blacklist
from django.contrib.auth.models import User

from .forms import promorForm, promeeForm

from django.core.validators import validate_email
from django.core.mail import send_mail

class PromView(View):

	template = 'make.html'

	def get(self, request, who):

		who = ("promisor", "promisee")[who == 'send']
		if who == 'promisor':
			form = promorForm()
			title = 'Make promise'
			btnvalue = 'Make promise'
		else:
			form = promeeForm()
			title = 'Send to promisor for approval'
			btnvalue = 'Submit promise'

		params = {
			'webcrawl': True,
			'title': title,
			'form': form,
			'btnvalue': btnvalue,
		}
		return render(request, self.template, params)


	def post(self, request, who):

		who = ("promisor", "promisee")[who == 'send']

		if who == 'promisor':
			form = promorForm(request.POST)
		else:
			form = promeeForm(request.POST)

		# if error, rebuilt title, buttons according to who
		if not form.is_valid():
			if who == 'promisor':
				title = 'Make promise'
				btnvalue = 'Make promise'
			else:
				title = 'Send to promisor for approval'
				btnvalue = 'Submit promise'

			params = {
				'title': title,
				'form': form,
				'btnvalue': btnvalue
			}
			return render(request, self.template, params)

		promorEmail = form.cleaned_data['emailpromor']
		promeeEmail = form.cleaned_data['emailpromee']
		details = form.cleaned_data['details']
		privacy = ('private', 'public')[form.cleaned_data['public']]


		# check for PROMOR email
		Upromor = User.objects.filter(email=promorEmail).first()

		# if not a user, create one
		if not Upromor:
			Upromor = User.objects.create(
				email = promorEmail,
				password = None,
				username = None,
				first_name = None,
				last_name = None,
				is_active = None,
			)

		# check for PROMEE email
		Upromee = User.objects.filter(email=promeeEmail).first()

		# if not a user, create one
		if not Upromee:
			Upromee = User.objects.create(
				email = promeeEmail,
				password = None,
				username = None,
				first_name = None,
				last_name = None,
				is_active = None,
			)
		# promeedecrypted = Encryption.decrypt(Upromee.email)


		# INSERT INTO promise
		prom = promise.objects.create(
			status = 'draft',
			privacy = privacy,
			details = details,
			promorid = User.objects.get(id=Upromor.id),
			promeeid = User.objects.get(id=Upromee.id),
		)


		# #################################################################
		# Encrypt email addresses for links
		# #################################################################
		# Promisor
		promorEmailEncrypt = Encryption.encrypt(promorEmail)

		# Promisee
		promeeEmailEncrypt = Encryption.encrypt(promeeEmail)


		# #################################################################
		# MAKE URLS
		# #################################################################
		host = request.get_host()
		promid = base36.dumps(prom.promid)

		# promor url
		promorid = base36.dumps(Upromor.id)
		promorUrl = host + '/' + promid + '/' + promorEmailEncrypt

		# promee url
		promeeid = base36.dumps(Upromee.id)
		promeeUrl = host + '/' + promid + '/' + promeeEmailEncrypt


		# #################################################################
		# customize display text and emails based on if this is the promisor or promisee
		# #################################################################
		if who == 'promisor':
			title = "Congratulations.\nAccountability improves quality of life!"
			promiseintro = "Your promise is"
			senderEmail = promorEmail
			receiverEmail = promeeEmail
			receiver = "promisee"
			senderUrl = promorUrl
			receiverUrl = promeeUrl
		else:
			title = 'Promise sent for approval'
			promiseintro = "You submitted this promise"
			senderEmail = promeeEmail
			receiverEmail = promorEmail
			receiver = "promisor"
			senderUrl = promeeUrl
			receiverUrl = promorUrl


		# #################################################################
		# SEND EMAILS HERE!!!!!!!!!!!!!
		# #################################################################
		senderContent = 'senderIs' + who.capitalize()
		receiverContent = 'receiverIs' + receiver.capitalize()

		# SEND EMAIL TO SENDER
		EmailApprove.sendEmail(senderEmail, receiverEmail, senderUrl, senderContent)

		# SEND EMAIL TO RECEIVER
		EmailApprove.sendEmail(receiverEmail, senderEmail, receiverUrl, receiverContent)

		# #################################################################


		message = (
			'Emails sent out. Both you and the ' + receiver + ' must approve this promise.\n'
			'Please check your email to confirm.'
		)

		params = {
			'title': title,
			'message': message,
			'promiseintro': promiseintro,
			'promise': details,
			'promorurl': promorUrl,
			'promeeurl': promeeUrl,
		}
		return render(request, self.template, params)


#
# Manage page. Where promisor/promisee approves and completes promise status.
#
def manage(request, promid, emailEncrypt):

	emailDecrypted = Encryption.decrypt(emailEncrypt)
	currentUrl = request.path
	promIdB36 = promid

	# convert ids to integers
	promid = base36.loads(promid)
	#assert False, promid

	# VERIFY emailDecrypted passed in URL
	cursor = connection.cursor()
	query = '''
		SELECT
			promorid_id,
			au1.email promoremail,
			promorapprdate,
			promeeid_id,
			au2.email promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate
		FROM promise p
		JOIN auth_user au1 ON p.promorid_id = au1.id
		JOIN auth_user au2 ON p.promeeid_id = au2.id
		WHERE p.promid = %s'''
	cursor.execute(query, [promid])
	row = cursor.fetchone()

	if row:
		(	promorid,
			promoremail,
			promorapprdate,
			promeeid,
			promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate) = row
	else:
		return redirect('/404/error/')


	# Who is this? the promisor, or promisee?
	if emailDecrypted == promoremail:
		who = 'promisor'
		other = 'promisee'
		otherEmail = promeeemail
		otherId = promeeid
	elif emailDecrypted == promeeemail:
		who = 'promisee'
		other = 'promisor'
		otherEmail = promoremail
		otherId = promorid
	else:
		return redirect('/404/error/')


	# if form was submitted, alter database and redirect back here
	if request.POST:

		do = request.POST['do'].lower()
		# 	do = 'approve'
		# 	do = 'deny'
		# 	do = 'fulfilled'
		# 	do = 'broken'

		if do == 'deny':
			# mark promise for DELETION
			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				mdate = current,
				status = 'delete'
			)

		elif who == 'promisor' and do == 'approve' and promorapprdate == None:
			if promeeapprdate:
				status = 'pending'
			else:
				status = 'draft' # redundant, but keep it for clarity

			#set database promorapprdate to now
			#update mdate too
			#promorapprdate to now

			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				promorapprdate = current,
				mdate = current,
				status = status
			)
			promorapprdate = current

		elif who == 'promisee' and do == 'approve' and promeeapprdate == None:
			if promorapprdate:
				status = 'pending'
			else:
				status = 'draft' # redundant, but keep it for clarity

			#if promorapprdate change status
			#set database promeeapprdate to now
			#promeeapprdate to now

			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				promeeapprdate = current,
				mdate = current,
				status = status
			)
			promeeapprdate = current

		elif who == 'promisee' and status == 'pending' and (do == 'broken' or do == 'fulfilled'):
			status = do

			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				mdate = current,
				status = status
			)
			mdate = current


		# ######################################################################
		# if promise changed to active or complete, notify other party
		# ######################################################################
		if status in ['pending', 'broken', 'fulfilled']:
			host = request.get_host()
			otherEmailEncrypt = Encryption.encrypt(otherEmail)
			otherUrl = host + '/' + promIdB36 + '/' + otherEmailEncrypt

			# if status changed to active/pending, send notification email to other
			if status == 'pending':
				EmailActive.sendEmail(otherEmail, emailDecrypted, otherUrl, other)

				# if promisee just activated the promise, send them a Reference email so they can come back later
				if who == 'promisee':
					currentHostUrl = host + currentUrl
					EmailActive.sendEmail(emailDecrypted, otherEmail, currentHostUrl, 'promiseeReference')

			else:
				# If status marked complete, send notification email to other/promisor
				EmailComplete.sendEmail(otherEmail, emailDecrypted, otherUrl, status)


		# redirect to current url so refresh won't ask to post again
		return redirect(currentUrl)
	# endif request.POST:

	title = 'Manage promise'
	message = ''
	#mdate = mdate.isoformat()
	buttontype = None

	if status == 'delete':
		# DELETE promise from database
		promise.objects.filter(promid=promid).delete()
		message += 'Promise does not exist anymore.'
	elif who == 'promisor':
		if status == 'draft' and promorapprdate is None:
			message += ('Promise not active. Click to approve this promise.\n'
				'You can also delete this promise.')
			# button for promisor to approve
			buttontype = 'approve'
		elif status == 'draft' and promeeapprdate is None:
			message += ('Promise not active. Promisee has not yet approved. We will notify you '
				'when the promisee has approved.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'pending':
			message += ('Promise is active and pending. Awaiting promisee to '
				'make decision.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'broken' or status == 'fulfilled':
			message += ('This promise was marked as "' + status.capitalize() + '" ' + onOrAt(mdate) +
						' <span data-utc="' + mdate.isoformat() + '" class="localtime"></span>.')
	elif who == 'promisee':
		if status == 'draft' and promeeapprdate is None:
			message += ('Promise not active. Click to approve this promise.\n'
				'You can also delete this promise.')
			# button for promisee to approve
			buttontype = 'approve'
		elif status == 'draft' and promorapprdate is None:
			message += ('Promise not active. Promisor has not yet approved. We will notify you '
				'when the promisor has approved.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'pending':
			# BUTTONS for Promise broken, or Promise fulfilled
			buttontype = 'complete'

			# if promisee just Approved the promise, tell them we sent them an email, else don't tell them
			difference = datetime.datetime.now(pytz.utc) - promeeapprdate

			if difference.seconds <= 20:
				message += ('Promise is now active! We just sent you an email. When the promisor has kept (or broken) '
					'this promise, click on the link in the email to come back here.')
			else:
				message += ('Promise is not yet complete. Click "Fulfilled" or "Broken" whenever you are ready.')
		elif status == 'broken' or status == 'fulfilled':
			#mdate = "2008-09-15T15:53:00+01:00"
			message = ('You marked this promise as "' + status.capitalize() + '" ' + onOrAt(mdate) +
						' <span data-utc="' + mdate.isoformat() + '" class="localtime"></span>.')

	#assert False, message

	params = {
		'promid': promid,
		'status': status.capitalize(),
		'details': details,
		'cdate': cdate,
		'title': title,
		'message': message,
		'buttontype': buttontype,
		'current_url': currentUrl,
	}
	template = 'manage.html'
	return render(request, template, params)

#
# Public page for everyone to view data for a promise
#
def public(request, promid):

	# convert id to integers
	promid = base36.loads(promid)

	# GET promise detail based on promid passed in URL
	cursor = connection.cursor()
	query = '''
		SELECT
			promorid_id,
			au1.email promoremail,
			promorapprdate,
			promeeid_id,
			au2.email promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate
		FROM promise p
		JOIN auth_user au1 ON p.promorid_id = au1.id
		JOIN auth_user au2 ON p.promeeid_id = au2.id
		WHERE p.privacy = 'public' AND p.promid = %s'''
	cursor.execute(query, [promid])
	row = cursor.fetchone()

	if row:
		(	promorid,
			promoremail,
			promorapprdate,
			promeeid,
			promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate) = row
	else:
		return redirect('/404/error/')

	params = {
		'status': status,
		'details': details,
		'privacy': privacy,
		'current': timezone.now(),
		'cdate': cdate,
		'mdate': mdate,
		#'promid': promid,
	}

	template = 'public.html'
	return render(request, template, params)




#####################################################################
# if user does not want to receive emails from us, blacklist it
#####################################################################
def blacklistEmail(request, emailEncrypt):

	template = 'blacklist.html'

	# see if a valid email has been passed in
	try:
		emailDecrypted = decrypt(emailEncrypt)
		can_decrypt = True
	except:
		can_decrypt = False

	try:
		validate_email(emailDecrypted)
		valid_email = True
	except:
		valid_email = False

	if not valid_email or not can_decrypt:
		message = "The email address given to us is gibberish. Nothing to blacklist."
		params = {
			'message': message,
		}
		return render(request, template, params)


	# see if the email address is already blacklisted
	Blacklist = blacklist.objects.filter(email=emailEncrypt).first()

	if Blacklist:
		message = "Email address has already been blacklisted."
	else:
		# Create entry
		Blacklist = blacklist.objects.create(
			email = emailEncrypt,
		)
		message = "Email blacklist successful. You will not hear from us again."

	params = {
		'message': message,
	}

	return render(request, template, params)



#
# For displaying a date or time: if within 24 hours, return "at"; otherwise "on"
#
def onOrAt(past_date):
	now = datetime.datetime.now(pytz.utc)
	difference = now - past_date

	# if date less than 24 hours, return "at"; otherwise return "on"
	if difference.days == 0:
		return "at"
	return "on"
