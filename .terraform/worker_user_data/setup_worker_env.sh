#!/bin/bash

cd /home/devops/

# Setup worker secrets
touch .env
echo "BROKER_URL=pyamqp://$(cat /opt/rabbitmq_user):$(cat /opt/rabbitmq_passwd)@gabate.h3nnn4n.me" >> .env
echo "RESULT_BACKEND=redis://$(cat /opt/redis_user):$(cat /opt/redis_passwd)@gabate.h3nnn4n.me" >> .env

# Setup aws credentials
mkdir .aws
echo "[default]
aws_access_key_id = $(cat /opt/aws_api_key)
aws_secret_access_key = $(cat /opt/aws_secret_key)\
" > .aws/credentials

chown -R devops:devops /home/devops/.aws/
