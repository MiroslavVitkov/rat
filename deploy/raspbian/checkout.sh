#!/usr/bin/env sh


# In this file: update rat's source code with GitHub as source of truth.
#               Notice .ssh/ and .git/ are not affected by the * operations.
#               Make sure to have the repo cloned in https mode.
#               Needs to be ran as root.


set -u  # error on using uninitialized variable


systemctl stop rat-listen

cd ~/proj/rat &&\
git pull &&\
python/rat.py test

if [ $? -eq 0 ]; then
    mv /opt/rat/conf.ini /tmp/
    cp -r ~/proj/rat/* /opt/rat/
    mv /tmp/conf.ini /opt/rat/
fi

systemctl start rat-listen
