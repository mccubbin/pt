from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
@login_required
def userProfile(request):
	user = request.user
	params = {user: 'user'}
	template = 'profile.html'
	return render(request, template, params)
