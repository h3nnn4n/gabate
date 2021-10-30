#!/bin/bash

IP="$(terraform output -json db_server_ip | jq --raw-output '.')"
USER=devops


ssh -o UserKnownHostsFile=/dev/null \
    -o StrictHostKeyChecking=no \
    -i ~/.ssh/tf-hetzner \
    $USER@$IP

while [[ $? -ne 1 ]]
do
  sleep 2
  ssh -o UserKnownHostsFile=/dev/null \
      -o StrictHostKeyChecking=no \
      -i ~/.ssh/tf-hetzner \
      $USER@$IP
done
