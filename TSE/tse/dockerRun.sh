docker run --rm --add-host dockerhost:192.168.65.2 \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/analysis_input.json:/analysis_input.json" \
-v "$(pwd)/security_input.json:/security_input.json" datasharing/tse:2019-09-30