#!/bin/sh

USER=$(cat /opt/rabbitmq_user)
PASS=$(cat /opt/rabbitmq_passwd)

echo $USER > /var/log/potato
echo $PASS > /var/log/potato

ls /usr/sbin/ > /var/log/ls_usr_sbin

echo $SHELL > /var/log/echo_shell
echo $PATH > /var/log/echo_path

which rabbitmqctl >> /var/log/setup_log
rabbitmqctl status > /var/log/rabbitmqctl_status2 2> /var/log/rabbitmqctl_status2_error
/usr/sbin/rabbitmqctl add_user $USER $PASS >> /var/log/setup_log 2>> /var/log/setup_log_errors
/usr/sbin/rabbitmqctl set_user_tags $USER administrator >> /var/log/setup_log 2>> /var/log/setup_log_errors
/usr/sbin/rabbitmqctl set_permissions -p / $USER ".*" ".*" ".*" >> /var/log/setup_log 2>> /var/log/setup_log_errors
