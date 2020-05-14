#!/bin/bash

#PARTY_NAMES=( "Party_1" "Party_2" "..." )
PARTY_NAMES=( "CBS" "DMS" )

for PARTY_NAME in ${PARTY_NAMES[@]}
do
  docker run \
    --rm \
    -it \
    --user $(id -u):$(id -g) \
    -e RUN="generate_receiver_keys" \
    -e PARTY_NAME="$PARTY_NAME" \
    -v "$(pwd)/input:/inputVolume" \
    -v "$(pwd)/output:/output" \
    datasharing:v2.0
done
