from django import template                                                                                                                                                        
import base36
import datetime


register = template.Library()


@register.filter
def space2dash(s):
	return s.replace(' ', '-')

@register.filter
def encode36(n):
	# Converts an integer to a base36 string.
	return base36.dumps(n)

@register.filter
def decode36(val):
	return base36.loads(val)




@register.simple_tag
def current_time():
    return datetime.datetime.now()


