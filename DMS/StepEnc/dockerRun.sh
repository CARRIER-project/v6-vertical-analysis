docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/DMSTestingData.csv:/DMSTestingData.csv" \
-v "$(pwd)/input.json:/input.json" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/encryption:/encryption" datasharing/dms_enc:2019-10-21
# :2019-09-30