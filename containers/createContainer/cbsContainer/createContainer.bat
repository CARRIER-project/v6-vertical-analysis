docker rm datasharing/cbs
docker build -t datasharing/cbs .\
echo. 2>%~dp0\output.txt
mkdir tmp
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output.txt:/output.txt -v %~dp0\tmp:/temp datasharing/cbs
docker push datasharing/cbs
