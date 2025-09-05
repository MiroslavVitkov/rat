#!/usr/bin/env sh

# In this file: update system settings and restart services on a raspbian system.
#               Needs to be run with root privileges.


set -u  # error on using uninitialized variable


# The parent dir of this script is the 'project'.
PROJDIR="$(dirname $0)"/../..


# $1 - service name as seen from systemctl
# $2 - source path in the repo hierarchy
# $3 - destination path within the server filesystem
update()
{
    DEST="$3"

    # No need to specify the filename for the destination, a directory suffices.
    if [ $(basename "$2") != $(basename "$3") ]; then
        DEST="$DEST"$(basename "$2")
    fi

    diff "$2" "$DEST" 1>/dev/zero 2>/dev/zero
    if [ "$?" -ne 0 -o ! -e "$DEST" ]; then
        echo "Updating $DEST"
        cp "$2" "$DEST"
        systemctl restart "$1"
    fi
}


update logrotate res/logrotate/rat /etc/logrotate.d/
update rat res/systemd/rat.service /etc/systemd/system/
update apache2 res/apache2/000-default.conf /etc/apache2/sites-enabled/

F2B_FILTER='/etc/fail2ban/filter.d/'
F2B_JAIL='/etc/fail2ban/jail.d/'
for file in res/f2b/*.conf; do
    update fail2ban "$file" "$F2B_FILTER"
done
for file in res/f2b/*.local; do
    update fail2ban "$file" "$F2B_JAIL"
done


pip install --break-system-packages -r "$PROJDIR"/python/requirements.txt
