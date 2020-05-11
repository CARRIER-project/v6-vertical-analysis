#!/bin/bash

#PARTY_NAMES=( "Party_1" "Party_2" "..." )
PARTY_NAMES=( "CBS" "DMS" )

mv output/SECRET*.key input/

for PARTY_NAME in ${PARTY_NAMES[@]}
do
  mv output/Public*"$PARTY_NAME".key ../"$PARTY_NAME"/input/
  mv ../"$PARTY_NAME"/output/Public*"$PARTY_NAME".key input/
  mv ../"$PARTY_NAME"/output/SECRET*"$PARTY_NAME".key ../"$PARTY_NAME"/input/
done
