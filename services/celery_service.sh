#you may need to run this from inside the repository folder and/or change the directory setting under program:celery
# (looks like almost all logging happens in celeryd.err)

#literally just run this script and celery will work.
# tails the celery log, ctrl-c to exit the tail

#sudo apt-get install -y rabbitmq-server
sudo pip install supervisor celery

#this is almost definitely overkill/unnecessary
sudo mkdir -p /etc/supervisor/conf.d/
sudo mkdir -p /var/log/celery/
sudo rm /var/log/celery/celeryd.log
sudo touch /var/log/celery/celeryd.log
sudo rm /var/log/celery/celeryd.err
sudo touch /var/log/celery/celeryd.err
sudo rm /var/log/supervisor/supervisord.log
sudo touch /var/log/supervisor/supervisord.log
sudo chmod 666 /var/log/celery/celeryd.err
sudo chmod 666 /var/log/celery/celeryd.log
sudo chmod 666 /var/log/supervisor/supervisord.log

sudo tee /etc/supervisord.conf >/dev/null <<EOL
[supervisord]
logfile = /var/log/supervisor/supervisord.log
logfile_maxbytes = 50MB
logfile_backups=10
loglevel = info
pidfile = /tmp/supervisord.pid
nodaemon = false
minfds = 1024
minprocs = 200
umask = 022
identifier = supervisor
directory = /tmp
childlogdir = /tmp
strip_ansi = false

[inet_http_server]
port = 127.0.0.1:50001

[supervisorctl]
serverurl = http://127.0.0.1:50001

[program:celery]
directory = /var/www/beiwe-backend/
command = celery -A celery_data_processing.data_processing_tasks worker --loglevel=info
stdout_logfile = /var/log/celery/celeryd.log
stderr_logfile = /var/log/celery/celeryd.err
autostart = true
EOL

echo "Use 'supervisord' or 'processing-start' to start the celery data processing service,"
echo "use 'killall supervisord' or 'processing-stop' to stop it."
echo "Note: you should not run supervisord as the superuser."
#supervisord
#tail -f /var/log/celery/celeryd.err