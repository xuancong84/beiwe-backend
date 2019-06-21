cd `dirname $0`
~/conda2/bin/python app.py 2>&1 | ~/conda2/bin/python -c "
import os,sys
while True:
	L=sys.stdin.readline()
	print >>sys.stdout, L.strip()
	print >>sys.stderr, L.strip()
	sys.stdout.flush()
	sys.stderr.flush()
" | gzip >>log.gz
