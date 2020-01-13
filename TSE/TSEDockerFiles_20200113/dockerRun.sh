docker run --rm \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/MLmodel.py:/MLmodel.py" \
-v "$(pwd)/analysis_input.json:/analysis_input.json" \
-v "$(pwd)/security_input.json:/security_input.json" datasharing/tse:2020-01-06