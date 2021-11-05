#!/bin/bash

REGION=us-east-1
IMAGE=gabate-worker
TAG=latest
REPOSITORY_NAME=${IMAGE}
REPOSITORY_URL=${TF_VAR_aws_account}.dkr.ecr.${REGION}.amazonaws.com
REPOSITORY=${REPOSITORY_URL}/${REPOSITORY_NAME}:${TAG}


aws ecr get-login-password --region ${REGION} | \
  docker login \
  --username AWS \
  --password-stdin ${REPOSITORY_URL}

docker build -t ${IMAGE} .

docker tag ${IMAGE} ${REPOSITORY}
docker push ${REPOSITORY}
