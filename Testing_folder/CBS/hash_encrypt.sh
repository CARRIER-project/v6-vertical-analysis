#!/bin/bash

DATA_FILE="20200511_sample_cbs.csv"

docker run \
  --rm \
  -it \
  --user $(id -u):$(id -g) \
  -e RUN="salt_hashing encrypt_data" \
  -v "$(pwd)/input:/inputVolume" \
  -v "$(pwd)/input/$DATA_FILE:/data_file.csv" \
  -v "$(pwd)/output:/output" \
  datasharing:v2.0
