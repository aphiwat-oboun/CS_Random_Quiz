"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.
Also creates an alias ``app`` for Vercel Serverless Python runtime.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

application = get_wsgi_application()
app = application
