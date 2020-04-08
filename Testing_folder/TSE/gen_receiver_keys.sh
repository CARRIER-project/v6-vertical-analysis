#!/bin/bash

docker run \
  --rm \
  -it \
  -e RUN="generate_receiver_keys" \
  -e PARTY_NAME="CBS" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0

docker run \
  --rm \
  -it \
  -e RUN="generate_receiver_keys" \
  -e PARTY_NAME="DMS" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
