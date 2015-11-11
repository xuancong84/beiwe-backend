# You can copy this file and paste it directly into ipython.
# tweak it as necessary for testing things.

# test these:
# ensure return data for voice recording is valid after json de/serialization

# tested as of 11/11/15:
# admin is not credentialed for this study (requires modifying a study)
# incorrect secret key
# admin dne
# invalid study id
# access key DNE/invalid
# user (patient) DNE/invalid


cpaste
import urllib, urllib2, locale
from flask import json
locale.setlocale(locale.LC_ALL, 'en_US')
print "\n\n"
def println(x): print x
e = Admins()[0] #Local debugging
access_key, secret_key = e.reset_access_credentials() #local debugging
url = 'http://localhost:8080/get-data/v1' #local debugging
# url = 'https://studies.beiwe.org/get-data/v1' #production debugging
values = {
          # 'access_key' : "IWz6ABsGxx9+NrgWquIM5wbm0gE1R11pKkfPS8/xhPhZo+LoszVXudhDAfVjlVbD", #production testing for eli user
          # 'secret_key' : "M1w1/EldtCw0hiE7Wi6VqVNiwCNlx/41SaSGqyrsnn9mCCBDGBkF0HlSVJhP5DY1", #production testing for eli user
          'access_key' : access_key,
          'secret_key' : secret_key,
          # 'access_key' : "steve", #invalid access key
          # 'secret_key' : "steve", #incorrect secret key
          'study_id' : '55d3826297013e3a1c9b8c3e', #study id for debugging study
          # 'study_id' : 'steve', #invalid study id
          'user_ids' : json.dumps(["h6fflp"]), #user id for eli's test user
          # 'user_ids' : json.dumps(["steve"]), #invalid user (patient) id
          'data_streams' : json.dumps(["wifiLog"])
          # "data_streams": json.dumps(['accel'])#,'bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog'])
          # "data_streams": json.dumps(['bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog'])
          }


req = urllib2.Request(url, urllib.urlencode(values))
# req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req)
# response = urllib2.urlopen(req, json.dumps(values))
page = response.read()
data = json.loads(the_page)
if the_page[:15] == "<!DOCTYPE html>":
	#Print out html but exclude lines consisting of only whitespace
	[println(line) for line in page.splitlines() if not line.isspace() and line]
else:
	#when return data is in the correct form from the api call, print out the length of the data.
	print "total size:", locale.format("%d", sum(len(key) + len(item) for key, item in data.items() ), grouping=True)
--

