#!/bin/bash

docker run \
  --rm \
  -it \
  -e RUN="generate_sender_keys" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing_exe:v2.0
