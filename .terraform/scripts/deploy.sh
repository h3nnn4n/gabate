#!/bin/bash

echo yes | terraform apply -var=hcloud_token=${HCLOUD_TOKEN}
