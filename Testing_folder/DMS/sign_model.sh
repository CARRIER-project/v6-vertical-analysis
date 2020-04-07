#!/bin/bash

docker run \
  --rm \
  -it \
  -e RUN="sign_model" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
