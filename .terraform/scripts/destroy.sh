#!/bin/bash

echo yes | terraform destroy -var=hcloud_token=${HCLOUD_TOKEN}
