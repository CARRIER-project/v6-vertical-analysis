docker run --rm \
-v "$(pwd)/input/encrypt_input.yaml:/inputVolume/encrypt_input.yaml" \
-v "$(pwd)/input/20200308_cbs.csv:/data_file.csv" \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" datasharing_encdata:local0.1


# docker run --rm \
# -v "$(pwd)/input/MLmodel_ave.py:/MLmodel_ave.py" \
# -v "$(pwd)/input/MLmodel_sum.py:/MLmodel_sum.py" \
# -v "$(pwd)/input/sign_model_input.yaml:/inputVolume/sign_model_input.yaml" \
# -v "$(pwd)/output:/output" datasharing_signmodel:local0.1

# docker run --rm \
# -v "$(pwd)/input:/inputVolume" \
# -v "$(pwd)/output:/output" datasharing_signmodel:local0.1
