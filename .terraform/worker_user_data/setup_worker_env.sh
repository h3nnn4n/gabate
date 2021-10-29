#!/bin/bash

cd /home/devops/

# Setup secrets
touch .env
echo "BROKER_URL=pyamqp://$(cat /opt/rabbitmq_user):$(cat /opt/rabbitmq_passwd)@$(cat /opt/db_server_ip)" >> .env
echo "RESULT_BACKEND=redis://$(cat /opt/db_server_ip)" >> .env
