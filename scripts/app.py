"""
Simple app.py file for deployment platforms that expect it.
This imports our Django WSGI application.
"""

from enhanced_timetable_system.wsgi import application

# Some platforms expect 'app' variable
app = application
