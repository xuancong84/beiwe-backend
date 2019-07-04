#!/usr/bin/env bash


cd `dirname $0`

~/conda3/bin/python app.py 2>&1 | ~/conda3/bin/python -c "
import os,sys
sys.stdin.reconfigure(encoding='ascii')
sys.stdout.reconfigure(encoding='ascii')
sys.stderr.reconfigure(encoding='ascii')
while True:
	L=sys.stdin.readline()
	print(L.strip(), file=sys.stdout, flush=True)
	print(L.strip(), file=sys.stderr, flush=True)
" | gzip >>log.gz
