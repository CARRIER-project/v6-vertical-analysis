docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/new_cbs_test_enc.csv:/new_cbs_test_enc.csv" \
-v "$(pwd)/input.json:/input.json" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/encryption:/encryption" datasharing/cbs_enc:2019-09-30