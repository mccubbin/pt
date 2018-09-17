#from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.views import View
import base36
import datetime
from django.utils import timezone

from classes.encryption import Encryption

from django.db import connection
from prom.models import promise, blacklist
from django.contrib.auth.models import User

from .forms import promerForm, promeeForm

from django.core.validators import validate_email
from django.core.mail import send_mail

class PromView(View):

	template = 'make.html'

	def get(self, request, who):

		who = ("promisor", "promisee")[who == 'send']
		if who == 'promisor':
			form = promerForm()
			title = 'Make promise'
			btnvalue = 'Make promise'
		else:
			form = promeeForm()
			title = 'Send to promisor for approval'
			btnvalue = 'Submit promise'
		#assert False, who

		params = {'title': title, 'form': form, 'btnvalue': btnvalue }
		return render(request, self.template, params)


	def post(self, request, who):
		who = ("promisor", "promisee")[who == 'send']
		if who == 'promisor':
			form = promerForm(request.POST)
			title = "Congratulations.\nAccountability improves quality of life!"
			promiseintro = "Your promise is"
			other = "recipient"
		else:
			form = promeeForm(request.POST)
			title = 'Promise sent for approval'
			promiseintro = "You submitted this promise"
			other = "promisor"
		#assert False, request

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

		emailpromer = form.cleaned_data['emailpromer']
		emailpromee = form.cleaned_data['emailpromee']
		details = form.cleaned_data['details']
		privacy = ('private', 'public')[form.cleaned_data['public']]


		# check for PROMER email
		promerencrypted = Encryption.encrypt(emailpromer)
		Upromer = User.objects.filter(email=promerencrypted).first()
		if not Upromer:
			Upromer = User.objects.create(
				email = promerencrypted,
				password = None,
				username = None,
				first_name = None,
				last_name = None,
				is_active = None,
			)
		promerdecrypted = Encryption.decrypt(Upromer.email)
		# print('hello ' + promerdecrypted + '.')


		# check for PROMEE email
		promeeencrypted = Encryption.encrypt(emailpromee)
		Upromee = User.objects.filter(email=promeeencrypted).first()
		if not Upromee:
			Upromee = User.objects.create(
				email = promeeencrypted,
				password = None,
				username = None,
				first_name = None,
				last_name = None,
				is_active = None,
			)
		promeedecrypted = Encryption.decrypt(Upromee.email)
		# print('hello ' + promeedecrypted + '.')


		# INSERT INTO promise
		prom = promise.objects.create(
			status = 'draft',
			privacy = privacy,
			details = details,
			promerid = User.objects.get(id=Upromer.id),
			promeeid = User.objects.get(id=Upromee.id),
		)



		# #################################################################
		# MAKE URLS
		# #################################################################
		promid = base36.dumps(prom.promid)

		# promerurl
		promerid = base36.dumps(Upromer.id)
		promerurl = '/crm/' + promid + '/' + promerid + '/' + Upromer.email

		# promeeurl
		promeeid = base36.dumps(Upromee.id)
		promeeurl = '/crm/' + promid + '/' + promeeid + '/' + Upromee.email


		# #################################################################
		# SEND EMAILS HERE!!!!!!!!!!!!!
		# #################################################################

		# #################################################################
		# PROMISOR SEND MAIL
		promertext = promerEmail(promerencrypted, promeedecrypted, promerurl, request)
		#assert False, request
		send_mail(
			'PromiseTracker: verify your promise.',
			promertext,
			"PromiseTracker<mail@PromiseTracker.com>",
			[promerdecrypted],
			fail_silently=False,
		)

		# #################################################################
		# PROMISEE SEND MAIL
		promeetext = promeeEmail(promeeencrypted, promerdecrypted, promeeurl, request)
		send_mail(
			'PromiseTracker: someone made a promise to you.',
			promeetext,
			"PromiseTracker<mail@PromiseTracker.com>",
			[promeedecrypted],
			fail_silently=False,
		)
		# #################################################################


		message = (
			'Emails sent out. Both you and the ' + other + ' '
			'must approve this promise.\n'
			'Please check your email to confirm.'
		)

		params = {
			'title': title,
			'message': message,
			'promiseintro': promiseintro,
			'promise': details,
			'promerurl': promerurl,
			'promeeurl': promeeurl,
		}
		return render(request, self.template, params)


def promerEmail(promerEncrypt, promeeEmail, promerUrl, request):
	host = request.get_host()
	text = """
You are making a promise to %s.

Click here to Approve your promise:

%s%s

After both have approved this promise, use the link above to view the status of your promise.

Thank you for using our free service,
PromiseTracker




To never receive another email from PromiseTracker.com, click here:
%s/bl/%s

""" % (promeeEmail, host, promerUrl, host, promerEncrypt)

	return text


def promeeEmail(promeeEncrypt, promerEmail, promeeUrl, request):
	host = request.get_host()
	text = """
%s is making a promise to you.

Click here to Approve this promise:

%s%s

After both parties have approved this promise, use the link above to mark this promise as "Fulfilled" or "Broken".

Thank you for using our free service,
PromiseTracker




To never receive another email from PromiseTracker.com, click here:
%s/bl/%s

""" % (promerEmail, host, promeeUrl, host, promeeEncrypt)
	return text


def manage(request, promid, uid, encemail):

	current_url = request.path

	# convert ids to integers
	promid = base36.loads(promid)
	uid = base36.loads(uid)

	# VERIFY uid and encemail passed in URL
	cursor = connection.cursor()
	query = '''
		SELECT
			promerid_id,
			au1.email promeremail,
			promerapprdate,
			promeeid_id,
			au2.email promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate
		FROM promise p
		JOIN auth_user au1 ON p.promerid_id = au1.id
		JOIN auth_user au2 ON p.promeeid_id = au2.id
		WHERE p.promid = %s'''
	cursor.execute(query, [promid])
	row = cursor.fetchone()

	if row:
		(	idpromer,
			empromer,
			promerapprdate,
			idpromee,
			empromee,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate) = row
	else:
		return redirect('/404/error/')


	# Who is this? the promisor, or promisee?
	if (uid == idpromer) and (encemail == empromer):
		promisor = True
		promisee = False
	elif (uid == idpromee) and (encemail == empromee):
		promisor = False
		promisee = True
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

		elif promisor and do == 'approve' and promerapprdate == None:
			if promeeapprdate:
				status = 'pending'
			else:
				status = 'draft'

			#set database promerapprdate to now
			#update mdate too
			#promerapprdate to now

			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				promerapprdate = current,
				mdate = current,
				status = status
			)
			promerapprdate = current

		elif promisee and do == 'approve' and promeeapprdate == None:
			if promerapprdate:
				status = 'pending'
			else:
				status = 'draft'
			#if promerapprdate change status
			#set database promeeapprdate to now
			#promeeapprdate to now
			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				promeeapprdate = current,
				mdate = current,
				status = status
			)
			promeeapprdate = current

		elif promisee and status == 'pending' and (do == 'broken' or do == 'fulfilled'):
			status = do

			current = timezone.now()
			promise.objects.filter(promid=promid).update(
				mdate = current,
				status = status
			)
			mdate = current

		# redirect to current url so refresh won't ask to post again
		return redirect(current_url)
	# endif request.POST:

	title = 'Manage promise'
	message = ''
	buttontype = None

	if status == 'delete':
		# DELETE promise from database
		promise.objects.filter(promid=promid).delete()
		message += 'Promise does not exist anymore.'
	elif promisor:
		if status == 'draft' and promerapprdate is None:
			message += ('Promise not active. Click to approve this promise.\n'
				'You can also delete this promise.')
			# button for promisor to approve
			buttontype = 'approve'
		elif status == 'draft' and promeeapprdate is None:
			message += ('Promise not active. Promisee '
				'has not yet approved.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'pending':
			message += ('Promise is active and pending. Awaiting promisee to '
				'make decision.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'broken' or status == 'fulfilled':
			message += ('This promise was marked as ' + status.capitalize() +
				' on ' + mdate.strftime('%H:%M%p %Z, %b %d, %Y') + '.')
	elif promisee:
		if status == 'draft' and promeeapprdate is None:
			message += ('Promise not active. Click to approve this promise.\n'
				'You can also delete this promise.')
			# button for promisee to approve
			buttontype = 'approve'
		elif status == 'draft' and promerapprdate is None:
			message += ('Promise not active. Promisor has not yet approved.')
			# refresh button
			buttontype = 'refresh'
		elif status == 'pending':
			message += ('Promise is active and pending. If complete, click '
				'to mark this promise as broken or fulfilled.')
			# BUTTONS for Promise broken, or Promise fulfilled
			buttontype = 'complete'
		elif status == 'broken' or status == 'fulfilled':
			message += ('You marked this promise as ' + status.capitalize() +
				' on ' + mdate.strftime('%H:%M%p %Z, %b %d, %Y') + '.')

	#assert False, message

	params = {
		'promid': promid,
		'status': status.capitalize(),
		'details': details,
		'cdate': cdate,
		'title': title,
		'message': message,
		'buttontype': buttontype,
		'current_url': current_url,
	}
	template = 'manage.html'
	return render(request, template, params)


def public(request, promid):

	# convert id to integers
	promid = base36.loads(promid)

	# VERIFY uid and encemail passed in URL
	cursor = connection.cursor()
	query = '''
		SELECT
			promerid_id,
			au1.email promeremail,
			promerapprdate,
			promeeid_id,
			au2.email promeeemail,
			promeeapprdate,
			privacy,
			status,
			details,
			cdate,
			mdate
		FROM promise p
		JOIN auth_user au1 ON p.promerid_id = au1.id
		JOIN auth_user au2 ON p.promeeid_id = au2.id
		WHERE p.privacy = 'public' AND p.promid = %s'''
	cursor.execute(query, [promid])
	row = cursor.fetchone()

	if row:
		(	idpromer,
			empromer,
			promerapprdate,
			idpromee,
			empromee,
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
		'promid': promid,
		'current': timezone.now(),
		'cdate': cdate,
		'mdate': mdate,
	}

	template = 'public.html'
	return render(request, template, params)




#####################################################################
# if user does not want to receive emails from us, blacklist it
#####################################################################
def blacklistEmail(request, encemail):

	template = 'blacklist.html'

	# see if a valid email has been passed in
	try:
		decryptedemail = decrypt(encemail)
		can_decrypt = True
	except:
		can_decrypt = False

	try:
		validate_email(decryptedemail)
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
	Blacklist = blacklist.objects.filter(email=encemail).first()

	if Blacklist:
		message = "Email address has already been blacklisted."
	else:
		# Create entry
		Blacklist = blacklist.objects.create(
			email = encemail,
		)
		message = "Email blacklist successful. You will not hear from us again."

	params = {
		'message': message,
	}

	return render(request, template, params)



