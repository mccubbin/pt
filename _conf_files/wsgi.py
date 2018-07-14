"""
WSGI config for prom project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application

sys.path.append("/var/www")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_conf_files.settings")

application = get_wsgi_application()
