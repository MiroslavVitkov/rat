#!/usr/bin/env sh

# In this file: install the RAT executable on a raspbian system.
#               Needs to run with root privileges.


set -e  # exit on error
set -o pipefail  # exit on error inside a pipe
set -u  # error on using uninitialized variable


PORTS={42666..42672}


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
ufw default deny incoming
ufw allow 22
for PORT in "$PORTS"; do
    ufw limit "$PORT"
done
ufw allow 'Apache Full'
a2enmod ssl
a2enmod headers
a2dismod -f autoindex  # disable directory listing
apt install libapache2-mod-security2
a2enmod security2
sed -i 's\SecRuleEngine DetectionOnly\SecRuleEngine On' /etc/modsecurity/modsecurity.conf
cp /res/default-ssl.conf /etc/apache2/sites-enabled

# Generate a key and write it to user.keypath.
sed -i 's\keypath = ~/.ssh/rat\keypath = /opt/rat/.ssh/rat\' /opt/rat/conf.ini
rat generate

# See the shiny errors.
systemctl start rat

ufw status
journalctl -u rat
nmap -p "$PORTS" localhost

nikto -h <url>
a2dismod -f autoindex
ufw status
journalctl -u rat
nmap -p "$PORTS" localhost

apt install certbot python3-certbot-apache
certbot --apache -d rat.pm -d www.rat.pm

# `ufw limit` works on the network level; fail2ban is smarter.
apt install fail2ban
cp res/apache.conf.jail /etc/fail2ban/jail.d/apache.conf
cp res/apache-404.conf.filter /etc/fail2ban/filter.d/apache-404.conf
cp res/modsec-scanners.conf.filter /etc/fail2ban/filter.d/modsec-scanners.conf
cp res/modsec-deny.filter /etc/fail2ban/filter.d/modsec-deny.conf
systemctl enable fail2ban

# Needed for Apache server monitoring tools.
a2dismod status

# Needed for serving localized content.
a2dismod negotiation

# Honeypot that watchs for attempts to access obviously sensitive files.
cp honeypot.conf /etc/fail2ban/filter.d/

# Diasable directory listing.
sed 's\Options Indexes FollowSymLinks\Options FollowSymLinks' /etc/apache2/apache2.conf
# or a2dismod autoindex
