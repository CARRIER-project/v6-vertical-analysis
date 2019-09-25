docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/request.json:/request.json" \
-v "$(pwd)/AV291v3.sav:/AV291v3.sav" \
-v "$(pwd)/output:/output" datasharing/dms_req