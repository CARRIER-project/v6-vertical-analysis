docker rm datasharing/cbs
docker build -t datasharing/cbs .\
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt datasharing/cbs
