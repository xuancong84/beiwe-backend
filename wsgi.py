import sys
sys.path.insert(0, '/var/www/scrubs')
sys.stdout = sys.stderr

from app import app as application