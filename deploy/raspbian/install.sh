#!/usr/bin/env sh

# In this file: install the RAT executable on a raspbian system.
#               Needs to run with root privileges.


set -e  # exit on error
set -o pipefail  # exit on error inside a pipe
set -u  # error on using uninitialized variable


PORTS=42666-42672


# A new user with no login, home or group.
adduser --system rat

# The parent dir of this script is the 'project'.
PROJDIR="$(dirname ${1})"
cp -r "$PROJDIR" /opt
rm -rf /opt/rat/.git

# Enable log rotation.
# The log is in the forest: /var/log/rat.log.
cp res/rat /etc/logrotate.d/rat

# Tell sysdemd to bring 'rat listen' up on boot
# and restart if it exits.
cp res/rat.service /etc/system/system/rat.service
systemctl enable rat

# You guys are going to love me(we're root)...
pip install --break-system-packages ffmpeg-python

# IF it will be facing the internet.
apt update && apt install ufw
ufw allow 22
for PORT in {"$PORTS"}; do
    ufw limit "$PORT"
done

# Generate a key and write it to user.keypath.
sed -i 's\keypath = ~/.ssh/rat\keypath = /opt/rat/.ssh/rat\' /opt/rat/conf.ini
rat generate

# See the shiny errors.
systemctl start rat

ufw status
journalctl -u rat
nmap -p "$PORTS" localhost
