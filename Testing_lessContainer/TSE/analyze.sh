#!/bin/bash

docker run \
  --rm \
  -it \
  -e RUN="verify_decrypt matching analysis_main" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/output:/output" \
  datasharing_exe:v2.0
