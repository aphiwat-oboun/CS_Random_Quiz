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

# Auto-migrate and seed for Vercel Serverless /tmp database
if os.environ.get("VERCEL"):
    try:
        from django.core.management import call_command
        from my_app.models import Question
        call_command("migrate", interactive=False)
        if Question.objects.count() == 0:
            call_command("seed_data")
    except Exception as e:
        print(f"[WSGI Init Notice] {e}")
