#!/usr/bin/env python2
# coding=utf-8

import os,sys,argparse,re,pytz
from datetime import datetime

if __name__=='__main__':
	parser = argparse.ArgumentParser(usage='$0 [options] 1>output 2>progress', description='This program converts timestamp')
	parser.add_argument('--field', '-f', help='timestamp is at Nth field (default=0)', type=int, default=0)
	parser.add_argument('--delimiter', '-d', help='timestamp is at Nth field (default=0)', type=str, default=',')
	parser.add_argument('--timezone', '-tz', help='timezone name (e.g., Singapore, PRC)', type=str, default='UTC')
	#nargs='?': optional positional argument; action='append': multiple instances of the arg; type=; default=
	opt=parser.parse_args()
	globals().update(vars(opt))

	tz = pytz.timezone(timezone)

	while True:
		try:
			L=raw_input()
		except:
			break

		try:
			its=L.split(delimiter)
			dt=datetime.fromtimestamp(float(its[field].strip())/1000.0).replace(tzinfo=pytz.utc)
			its[field]=str(dt.astimezone(tz=tz))[:23]
			print delimiter.join(its)
		except:
			print L

		sys.stdout.flush()
