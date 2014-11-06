import sys
sys.path.insert(0, '/var/www/beiwe')
sys.stdout = sys.stderr

from app import app as application
