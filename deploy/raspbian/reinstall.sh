#!/usr/bin/env sh

# In this file: update system settings and restart services on a raspbian system.
#               Needs to be run with root privileges.


set -e  # exit on error
#set -o pipefail  # exit on error inside a pipe; unsupported under dash shell
set -u  # error on using uninitialized variable


# The parent dir of this script is the project/.
PROJDIR="$(dirname $0)"/../..


# $1 - service name as seen from systemctl
# $2 - source path in the repo hierarchy
# $3 - destination path within the server filesystem
update()
{
    FILE=$(basename "$2")
    if [ 1 = 1 ]
#    if [ $(diff "$2" "$3") ]
#    if [ $(diff "$2" "$3") && $(diff "$2" "$3"/"$FIE") ]
    then
        
        systemctl restart "$1"
    fi
}


update logrotate res/rat.logrotate /etc/logrotate.d/rat
update rat res/rat.service /etc/systemd/system/rat.service

F2B_DIR=/etc/fail2ban/filter.d/
update fail2ban res/f2b/apache-404.conf "$F2B_DIR"
update fail2ban res/d2b/modsec-scanners.conf "$F2B_DIR"
update fail2ban res/f2b/modsec-deny.conf "$F2B_DIR"

pip install --break-system-packages -r "$PROJDIR"/python/requirements.txt
