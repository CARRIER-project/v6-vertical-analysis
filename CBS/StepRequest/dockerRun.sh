docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/request.json:/request.json" \
-v "$(pwd)/new_cbs_test.csv:/new_cbs_test.csv" \
-v "$(pwd)/output:/output" datasharing/cbs_basicinfo