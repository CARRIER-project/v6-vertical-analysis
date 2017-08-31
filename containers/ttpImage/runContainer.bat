rmdir /Q /S output
mkdir output

docker rm datasharing/ttp
docker build -t datasharing/ttp .\
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/output -v %~dp0\input.json:/input.txt datasharing/ttp