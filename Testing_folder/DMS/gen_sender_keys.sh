#!/bin/bash

docker run \
  --rm \
  -it \
  -e RUN="generate_sender_keys" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
