rmdir /Q /S output
mkdir output

docker rm datasharing/tse
docker build -t datasharing/tse .\
docker push datasharing/tse
rem docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/output -v %~dp0\input.json:/input.txt datasharing/ttp