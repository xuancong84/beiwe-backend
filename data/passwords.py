PASSWORD = "abcdefghijklmnopqrstuvwxyz012345"

MONGO_USERNAME = "beiwe"
MONGO_PASSWORD = "PhWY9uFaXScfU4uZeQXd"
MONGO_SECRET_KEY = '\xb7BdD<\x11\x80\xe9\x01\xdb\x19\xba\xff\xa5&\xef8\x13\xfb\xa8vA\x190'

"""
import mongolia
mongolia.add_user( "beiwe", "PhWY9uFaXScfU4uZeQXd" )
mongolia.authenticate_connection( "beiwe", "PhWY9uFaXScfU4uZeQXd" )

if you have set up a different default location for the conf,go edit it. otherwiseq:
cd to /etc, edit mongodb.conf using superuser privilages
find the line #auth=true and remove the commen (remove the #)
sudo service mongod restart
"""
