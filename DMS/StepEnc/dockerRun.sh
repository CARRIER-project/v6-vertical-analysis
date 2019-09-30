docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/new_dms_test_enc.csv:/new_dms_test_enc.csv" \
-v "$(pwd)/input.json:/input.json" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/encryption:/encryption" datasharing/dms_enc:2019-09-30