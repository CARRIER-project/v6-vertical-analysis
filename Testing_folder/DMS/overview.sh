#!/bin/bash

DATA_FILE="20200402_random_dms.csv"

docker run \
  --rm \
  -it \
  -e RUN="overview_request" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/input/$DATA_FILE:/data_file.csv" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
