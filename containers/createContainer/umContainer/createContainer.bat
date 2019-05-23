docker rm datasharing/um
docker build -t datasharing/um .\
echo. 2>%~dp0\output.txt
mkdir tmp
mkdir output
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt -v %~dp0\output:/output -v %~dp0\tmp:/temp datasharing/um
docker push datasharing/um
