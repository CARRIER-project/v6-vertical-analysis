#!/bin/bash

PARTY_NAME=DMS

docker run \
  --rm \
  -it \
  -e RUN="generate_sender_keys" \
  -e PARTY_NAME="$PARTY_NAME" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
