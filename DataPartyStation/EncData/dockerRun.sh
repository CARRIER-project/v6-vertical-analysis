docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/data_party_1.csv:/data_party_1.csv" \
-v "$(pwd)/encrypt_input.yaml:/encrypt_input.yaml" \
-v "$(pwd)/output:/output" datasharing_party:v0.1