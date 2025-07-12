#!/usr/bin/env bash


# In this file: query IPS status.


for i in $(fail2ban-client status | grep "Jail list" | cut -d: -f2 | tr ',' ' '); do
    fail2ban-client status "$i";
done
