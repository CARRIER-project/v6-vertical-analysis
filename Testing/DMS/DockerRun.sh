# docker run --rm \
# -v "$(pwd)/input/request.yaml:/inputVolume/request.yaml" \
# -v "$(pwd)/input/20200308_dms.csv:/data_file.csv" \
# -v "$(pwd)/output:/output" datasharing_overview:local0.1


docker run --rm \
-v "$(pwd)/input/20200309_dms.csv:/data_file.csv" \
-v "$(pwd)/input/encrypt_input.yaml:/inputVolume/encrypt_input.yaml" \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" datasharing_encdata:local0.1
# -v "$(pwd)/input/publicKey_dms.pem:/publicKey.pem" \

# docker run --rm \
# -v "$(pwd)/input/MLmodel_ave.py:/MLmodel_ave.py" \
# -v "$(pwd)/input/MLmodel_sum.py:/MLmodel_sum.py" \
# -v "$(pwd)/input/sign_model_input.yaml:/inputVolume/sign_model_input.yaml" \
# -v "$(pwd)/output:/output" datasharing_signmodel:local0.1
