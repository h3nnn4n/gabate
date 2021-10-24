#!/bin/bash

echo yes | terraform apply -var=hcloud_token=${HCLOUD_TOKEN}
sleep 5

IP=$(terraform output -json workers_servers_ips | jq --raw-output '."worker-0"')
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
