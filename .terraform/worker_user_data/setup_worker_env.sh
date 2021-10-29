#!/bin/bash

cd /home/devops/gabate/worker/

cat /opt/db_server_ip

# Setup secrets
touch .env
echo "BROKER_URL=pyamqp://gabate:PASSWD_HERE@$(cat /opt/db_server_ip)" >> .env
echo "RESULT_BACKEND=redis://$(cat /opt/db_server_ip)" >> .env

# Run celery
su devops -l -c "cd /home/devops/gabate/worker/ && /home/devops/.poetry/bin/poetry run celery -A tasks worker --loglevel=INFO --detach -f celery.logs"
