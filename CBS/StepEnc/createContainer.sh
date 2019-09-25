docker rmi datasharing/cbs_enc
docker build -t datasharing/cbs_enc .\

# Optional execution of container included
#docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt datasharing/um
