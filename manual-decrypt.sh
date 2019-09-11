
if [ $# -lt 2 ]; then
	echo "Usage: $0 input-folder output-folder [\"encryption-key-options\"]" >&2
	exit 1
fi

IN_PATH="$1"
OUT_PATH="$2"
if [ ! "$3" ]; then
	KEY_OPTION="$1"
else
	KEY_OPTION="$3"
fi


pycode="
import os, sys, argparse

import jinja2
from flask import Flask, render_template, redirect
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from config import load_django

from api import (participant_administration, admin_api, copy_study_api, data_access_api, data_pipeline_api, mobile_api, survey_api)
from config.settings import SENTRY_ELASTIC_BEANSTALK_DSN, SENTRY_JAVASCRIPT_DSN
from libs.admin_authentication import is_logged_in
from libs.security import set_secret_key
from pages import (admin_pages, mobile_pages, survey_designer, system_admin_pages, data_access_web_form)
from libs import encryption

from database.models import Study, DecryptionKeyError, EncryptionErrorMetadata, LineEncryptionError

parser = argparse.ArgumentParser(usage='$0 study_id <encrypted-input 1>decrypted-output', description='perform master-key decryption')
parser.add_argument('study_id', help='study_id')
parser.add_argument('-key', help='use encryption key', action='store_true')
opt = parser.parse_args()
globals().update(vars(opt))

if len(study_id)!=32:
	for s in study_id.split('/')[::-1]:
		if Study.objects.filter(object_id=s):
			study_id=s
			print >>sys.stderr, 'Auto-detected Study ID = '+study_id
			break

while True:
	L = sys.stdin.readline()
	if L == '':
		break
	fn_in, fn_out = L.strip().split('\t')
	try:
		if os.stat(fn_out).st_size>0:
			continue
	except:
		pass

	with open(fn_in) as fp_in:
		data = fp_in.read()

	with open(fn_out, 'w') as fp_out:
		if key:
		    fp_out.write(encryption.decrypt_server_by_key(data, study_id))
		else:
		    fp_out.write(encryption.decrypt_server(data, study_id))
	print >>sys.stderr, '.',
	sys.stderr.flush()
"

mkdir -p $OUT_PATH

prelen=${#IN_PATH}
find "$IN_PATH" -iname '*.csv' \
	| while read infn; do
		insuf=${infn:prelen}
		outfn=$OUT_PATH/$insuf
		mkdir -p `dirname $outfn`
		if [ -d "$infn" ]; then
			infn=$infn"/.dummys3_content"
		fi
		echo -e "$infn\t$outfn"
	done | ~/conda2/bin/python -c "$pycode" $KEY_OPTION
echo

