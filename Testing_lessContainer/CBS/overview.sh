#!/bin/bash

DATA_FILE="20200402_sample_cbs.csv"

docker run \
  --rm \
  -it \
  -e RUN="overview_request" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/input/$DATA_FILE:/data_file.csv" \
  -v "$(pwd)/output:/output" \
  datasharing_exe:v2.0
