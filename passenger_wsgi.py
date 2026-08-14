"""
Entry point required by cPanel's "Setup Python App" feature (Passenger),
used by Hostinger, Bluehost, and most other shared-hosting cPanel providers.

When you create the Python App in cPanel, set:
  - Application startup file:  passenger_wsgi.py
  - Application Entry point:   application   (the variable below)

See DEPLOYMENT.md at the project root for the full step-by-step setup.
"""
import os
import sys

# cPanel's Python App runs from the "Application root" you configure — this
# ensures the project directory is importable regardless of the working
# directory Passenger launches from.
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
