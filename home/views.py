from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from .forms import contactForm
#from django.http import HttpResponse

from prom.models import promise

def index(request):

	promcount = promise.objects.count()
	params = {
		'webcrawl': True,
		'promcount': promcount,
	}

	template = 'home.html'
	return render(request, template, params)

def example(request):
	params = {}
	template = 'example.html'
	return render(request, template, params)

def contact(request):
	title = 'Contact'
	form = contactForm(request.POST or None)
	confirm_message =  None
	#assert False, request

	if form.is_valid():
		name = form.cleaned_data['name']
		comment = form.cleaned_data['comment']
		userEmail = form.cleaned_data['email']
		subject = name + ': Comment about PromiseTracker'
		message = '%s\n\n%s\n%s' %(comment, name, userEmail)
		emailFrom = "PromiseTracker<comment@PromiseTracker.com>"
		emailTo = ["pd.mccubbin@gmail.com"]

		send_mail(
			subject,
			message,
			emailFrom,
			emailTo,
			fail_silently=False,
		)

		title = "Thanks!"
		confirm_message = "Your feedback is valued."
		form = None

	params = {'title': title, 'form': form, 'confirm_message': confirm_message }
	template = 'contact.html'
	return render(request, template, params)
	#return render(request, 'promise/contact.html', {'xyz':['Hi, if you want to contact me, send me an email', 'pd.mccubbin@gmail.com']})

def about(request):
	params = {}
	template = 'about.html'
	return render(request, template, params)

