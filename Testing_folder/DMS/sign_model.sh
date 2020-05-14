#!/bin/bash

docker run \
  --rm \
  -it \
  --user $(id -u):$(id -g) \
  -e RUN="sign_model" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
