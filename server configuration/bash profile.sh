#!/bin/bash

# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

#Alias aliases
alias a="alias"
alias p="nano ~/.profile; source ~/.profile"

#File Sizes
alias mongosize="ll -h /var/lib/mongodb/" #prints out the contents with file sizes of the mongodb folder
alias duu="du -d 1 -ha | sort -h"

#Swap
alias createswap="sudo fallocate -l 2560M /swapfile; sudo chmod 600 /swapfile; sudo mkswap /swapfile; sudo swapon /swapfile; swapon -s"
alias deleteswap="sudo swapoff /swapfile; sudo rm /swapfile"

#Bash Utility
alias sudo="sudo " # allows the use of all our aliases with the sudo command
alias n='nano -c'
alias sn='sudo nano -c'
alias ls='ls -h --color=auto'
alias ll='ls -l'
alias lh='ls -lX --color=auto'
alias lll="du -ah --max-depth=0 --block-size=MB --time * | sort -nr"
alias slll="sudo du -ah --max-depth=0 --block-size=MB --time * | sort -nr"
alias h="cd ~; clear; ls -X; echo"
alias grep='grep --color=auto'
alias u="cd .."
alias uu="cd ../.."
alias uuu="cd ../../.."

#Tools with CL config
alias htop="htop -d 5"
alias nload="nload -a 5 -i 80000 -o 80000"
alias df="df -h"

#Git
alias s='git status'
alias gs='git status'
alias pull="git pull"
alias master="git checkout master"
alias prod="git checkout production"


#File locations
alias www='cd /var/www/beiwe-backend'
alias apache="cd /etc/apache2"

#Apache restart functionality
alias apacherestart='sudo /etc/init.d/apache2 restart'
alias are='apacherestart'
alias restart='sudo service apache2 restart'
alias pyc='find . -type f -name "*.pyc" -delete -print'
alias up='update'
alias update='cd /var/www/beiwe-backend; pyc; git pull; touch /var/www/beiwe-backend/wsgi.py'

#Logs
alias logt='tail -f /var/log/apache2/error.log | cut -d " " -f 4,10-' #tail follow apache log
alias log='nano +1000000000 /var/log/apache2/error.log' #open log, go to end
alias logm='nano +1000000000 /var/log/mongodb/mongodb.log' #open mongo log, go to end
alias logmt='tail -f /var/log/mongodb/mongodb.log' #tail follow mongo log

alias relog='restart; logt'
alias uplog='up;logt'

#Configuration files
alias conf='sudo nano /etc/apache2/sites-enabled/beiwe.org.conf'
alias monconf='sudo nano /etc/mongodb.conf'
alias nanorc="nano ~/.nanorc"

#Services configuration files
alias boot="sudo sysv-rc-conf"

#Developer tools
alias db='cd /var/www/beiwe-backend/; ipython -i /var/www/beiwe-backend/db_shell.py'
alias sdb="cd /var/www/beiwe-backend/; sudo ipython -i /var/www/beiwe-backend/db_shell.py"
alias py="python"
alias ipy="ipython"

function run {
    nohup python -u $1 > ~/$1_log.out &
}


## Environment config ##

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi


# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
    . "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/bin" ] ; then
    PATH="$HOME/bin:$PATH"
fi

#makes the current git branch visible
function parse_git_branch () {
       git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}
RED="\[\033[0;31m\]"
YELLOW="\[\033[0;33m\]"
GREEN="\[\033[0;32m\]"
NO_COLOUR="\[\033[0m\]"
PS1="$GREEN\u$NO_COLOUR:\w$YELLOW\$(parse_git_branch)$NO_COLOUR\$ "
