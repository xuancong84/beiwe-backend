cd `dirname $0`
~/conda2/bin/python app.py 2>&1 | python3 -c "
import os,sys
while True:
	L=sys.stdin.readline()
	print(L.strip(), file=sys.stderr, flush=True)
	print(L.strip(), file=sys.stdout, flush=True)
" | gzip >>log.gz
