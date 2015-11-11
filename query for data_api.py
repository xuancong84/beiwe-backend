cpaste
import urllib, urllib2, locale
from flask import json
locale.setlocale(locale.LC_ALL, 'en_US')

print "\n\n\n"
def println(x): print x

# IWz6ABsGxx9+NrgWquIM5wbm0gE1R11pKkfPS8/xhPhZo+LoszVXudhDAfVjlVbD
# M1w1/EldtCw0hiE7Wi6VqVNiwCNlx/41SaSGqyrsnn9mCCBDGBkF0HlSVJhP5DY1

e = Admins()[0]
access_key, secret_key = e.reset_access_credentials()
# url = 'https://studies.beiwe.org/get-data/v1'
url = 'http://localhost:8080/get-data/v1'
values = {
          # 'access_key' : "IWz6ABsGxx9+NrgWquIM5wbm0gE1R11pKkfPS8/xhPhZo+LoszVXudhDAfVjlVbD",
          # 'secret_key' : "M1w1/EldtCw0hiE7Wi6VqVNiwCNlx/41SaSGqyrsnn9mCCBDGBkF0HlSVJhP5DY1",
          'access_key' : access_key,
          'secret_key' : secret_key,
          'study_id' : '55d3826297013e3a1c9b8c3e',
          'user_ids' : json.dumps(["h6fflp"]),
          'data_streams' : json.dumps(["wifiLog"])
          # "data_streams": json.dumps(['accel'])#,'bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog'])
          #"data_streams": json.dumps(['bluetoothLog','callLog','gps','identifiers','powerState','surveyTimings','textsLog'])
          }

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
# req.add_header('Content-Type', 'application/json')
response = urllib2.urlopen(req)
# response = urllib2.urlopen(req, json.dumps(values))
the_page = response.read()
the_data = json.loads(the_page)
if the_page[:15] == "<!DOCTYPE html>":
	[println(line) for line in the_page.splitlines() if not line.isspace() and line]
else:
	print "total size:", locale.format("%d", sum(len(key) + len(item) for key, item in the_data.items() ), grouping=True)
--

