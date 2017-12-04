docker rmi datasharing/um
docker build -t datasharing/um .\

# Optional execution of container included
#docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt datasharing/um
