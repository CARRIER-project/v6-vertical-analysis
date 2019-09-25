docker rmi datasharing/cbs_req
docker build -t datasharing/cbs_req .\

# Optional execution of container included
#docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt datasharing/um
