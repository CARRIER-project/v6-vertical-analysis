docker run --rm \
-v "$(pwd)/OnlyEnc/encrypt_input.yaml:/inputVolume/encrypt_input.yaml" \
-v "$(pwd)/OnlyEnc/20200309_dms_toCBS.csv:/data_file.csv" \
-v "$(pwd)/OnlyEnc/publicKey_dms.pem:/publicKey.pem" \
-v "$(pwd)/output:/output" datasharing_enconly:local0.1