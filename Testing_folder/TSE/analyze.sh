#!/bin/bash

docker run \
  --rm \
  -it \
  --user $(id -u):$(id -g) \
  -e RUN="verify_decrypt matching analysis_main" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
