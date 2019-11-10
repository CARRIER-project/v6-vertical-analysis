docker run --rm \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/analysis_input_cat.json:/analysis_input.json" \
-v "$(pwd)/security_input.json:/security_input.json" datasharing/tse:2019-10-31